"""
Orders Views
Cart management, checkout process, and order viewing.
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, TemplateView

from apps.accounts.models import Address
from apps.products.models import Product

from .models import Cart, CartItem, Order, OrderItem, OrderStatus


class CartMixin:
    """Mixin to get or create cart for the current request."""
    
    def get_cart(self):
        """Get or create cart for the current user/session."""
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                user=None
            )
        return cart


class CartDetailView(CartMixin, TemplateView):
    """Display cart contents."""
    
    template_name = "orders/cart.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = self.get_cart()
        return context


class CartAddView(CartMixin, View):
    """Add a product to the cart."""
    
    def post(self, request, product_slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=product_slug, is_active=True)
        
        quantity = int(request.POST.get("quantity", 1))
        variant_id = request.POST.get("variant_id")
        
        variant = None
        if variant_id:
            variant = product.variants.filter(id=variant_id, is_active=True).first()
        
        # Check stock
        if product.track_inventory:
            available_stock = variant.stock_quantity if variant else product.stock_quantity
            if available_stock < quantity:
                messages.error(
                    request,
                    _("Sorry, only %(stock)d items available.") % {"stock": available_stock}
                )
                return redirect("products:product_detail", slug=product_slug)
        
        cart = self.get_cart()
        cart.add_item(product, quantity, variant)
        
        messages.success(
            request,
            _("%(product)s has been added to your cart.") % {"product": product.name}
        )
        
        redirect_url = request.POST.get("redirect_url", "orders:cart_detail")
        return redirect(redirect_url)


class CartRemoveView(CartMixin, View):
    """Remove an item from the cart."""
    
    def post(self, request, item_id, *args, **kwargs):
        cart = self.get_cart()
        cart.remove_item(item_id)
        messages.success(request, _("Item removed from cart."))
        return redirect("orders:cart_detail")


class CartUpdateView(CartMixin, View):
    """Update cart item quantity."""
    
    def post(self, request, item_id, *args, **kwargs):
        cart = self.get_cart()
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        quantity = int(request.POST.get("quantity", 1))
        
        # Check stock
        product = item.product
        if product.track_inventory:
            available_stock = item.variant.stock_quantity if item.variant else product.stock_quantity
            if quantity > available_stock:
                messages.error(
                    request,
                    _("Only %(stock)d items available.") % {"stock": available_stock}
                )
                return redirect("orders:cart_detail")
        
        item.update_quantity(quantity)
        messages.success(request, _("Cart updated."))
        return redirect("orders:cart_detail")


class CartClearView(CartMixin, View):
    """Clear all items from the cart."""
    
    def post(self, request, *args, **kwargs):
        cart = self.get_cart()
        cart.clear()
        messages.success(request, _("Cart cleared."))
        return redirect("orders:cart_detail")


class CheckoutView(CartMixin, LoginRequiredMixin, View):
    """Checkout process view."""
    
    template_name = "orders/checkout.html"
    
    def get_cart(self):
        """Get cart for authenticated user only."""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    def get(self, request, *args, **kwargs):
        cart = self.get_cart()
        
        if not cart.items.exists():
            messages.warning(request, _("Your cart is empty."))
            return redirect("orders:cart_detail")
        
        # Get user's addresses
        addresses = request.user.addresses.all()
        default_address = addresses.filter(is_default=True).first()
        
        return render(request, self.template_name, {
            "cart": cart,
            "addresses": addresses,
            "default_address": default_address,
        })
    
    def post(self, request, *args, **kwargs):
        cart = self.get_cart()
        
        if not cart.items.exists():
            messages.warning(request, _("Your cart is empty."))
            return redirect("orders:cart_detail")
        
        # Get address selection
        address_id = request.POST.get("address_id")
        use_new_address = True
        
        if use_new_address:
            # Create new address
            shipping_address = {
                "full_name": request.POST.get("shipping_full_name"),
                "street_address_1": request.POST.get("shipping_street_address_1"),
                "street_address_2": request.POST.get("shipping_street_address_2", ""),
                "city": request.POST.get("shipping_city"),
                "state_province": request.POST.get("shipping_state_province"),
                "postal_code": request.POST.get("shipping_postal_code"),
                "country": request.POST.get("shipping_country", "US"),
                "phone": request.POST.get("shipping_phone", ""),
            }
        elif address_id:
            address = get_object_or_404(Address, id=address_id, user=request.user)
            shipping_address = {
                "full_name": address.full_name,
                "street_address_1": address.street_address_1,
                "street_address_2": address.street_address_2,
                "city": address.city,
                "state_province": address.state_province,
                "postal_code": address.postal_code,
                "country": address.country,
                "phone": address.phone_number,
            }
        else:
            messages.error(request, _("Please select or enter a shipping address."))
            return redirect("orders:checkout")
        
        # Calculate totals
        subtotal = cart.subtotal
        shipping_cost = cart.shipping_cost
        tax_amount = Decimal("0.00")  # Tax calculation would go here
        discount_amount = Decimal("0.00")  # Discount calculation would go here
        total = subtotal + shipping_cost + tax_amount - discount_amount
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            email=request.user.email,
            status=OrderStatus.PENDING,
            **{f"shipping_{k}": v for k, v in shipping_address.items()},
            billing_same_as_shipping=True,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total=total,
            currency="USD",
            customer_note=request.POST.get("customer_note", ""),
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                variant_name=cart_item.variant.name if cart_item.variant else "",
                unit_price=cart_item.unit_price,
                quantity=cart_item.quantity,
            )
            
            # Decrease stock
            if cart_item.product.track_inventory:
                cart_item.product.decrease_stock(cart_item.quantity)
        
        # Clear cart
        cart.clear()
        
        # Redirect to payment
        return redirect("orders:checkout_success", order_number=order.order_number)
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class CheckoutSuccessView(LoginRequiredMixin, DetailView):
    """Display order confirmation after successful checkout."""
    
    model = Order
    template_name = "orders/checkout_success.html"
    context_object_name = "order"
    slug_url_kwarg = "order_number"
    slug_field = "order_number"
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    """Display order details."""
    
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"
    slug_url_kwarg = "order_number"
    slug_field = "order_number"
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


# =============================================================================
# CONTEXT PROCESSORS
# =============================================================================

def cart_item_count(request):
    """
    Add cart item count to all template contexts.
    
    Returns:
        dict with 'cart_item_count' key.
    """
    count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.item_count
        except Cart.DoesNotExist:
            pass
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key, user=None)
                count = cart.item_count
            except Cart.DoesNotExist:
                pass
    
    return {"cart_item_count": count}
