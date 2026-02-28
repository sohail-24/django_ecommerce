"""
Orders Models
Cart, Order, and OrderItem models with full order lifecycle management.
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel
from apps.products.models import Product, ProductVariant


class OrderStatus(models.TextChoices):
    """Order status choices for lifecycle management."""
    
    PENDING = "pending", _("Pending")
    PAID = "paid", _("Paid")
    PROCESSING = "processing", _("Processing")
    SHIPPED = "shipped", _("Shipped")
    DELIVERED = "delivered", _("Delivered")
    CANCELLED = "cancelled", _("Cancelled")
    REFUNDED = "refunded", _("Refunded")


class Cart(TimeStampedModel):
    """
    Shopping cart model supporting both guest and authenticated users.
    
    Features:
    - Session-based for guests
    - User-based for authenticated users
    - Automatic cart merging on login
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
        verbose_name=_("user")
    )
    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("session key")
    )
    
    class Meta:
        verbose_name = _("cart")
        verbose_name_plural = _("carts")
        indexes = [
            models.Index(fields=["user", "session_key"]),
        ]
    
    def __str__(self):
        if self.user:
            return f"Cart - {self.user.email}"
        return f"Cart - {self.session_key[:20]}..."
    
    @property
    def item_count(self):
        """Return total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Calculate cart subtotal."""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def shipping_cost(self):
        """Calculate shipping cost based on subtotal."""
        if self.subtotal >= settings.FREE_SHIPPING_THRESHOLD:
            return Decimal("0.00")
        return settings.FLAT_SHIPPING_RATE
    
    @property
    def total(self):
        """Calculate cart total including shipping."""
        return self.subtotal + self.shipping_cost
    
    def add_item(self, product, quantity=1, variant=None):
        """Add a product to the cart."""
        item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            variant=variant,
            defaults={"quantity": quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return item
    
    def remove_item(self, item_id):
        """Remove an item from the cart."""
        self.items.filter(id=item_id).delete()
    
    def clear(self):
        """Remove all items from the cart."""
        self.items.all().delete()
    
    def merge_with(self, other_cart):
        """Merge another cart into this one."""
        for item in other_cart.items.all():
            self.add_item(item.product, item.quantity, item.variant)
        other_cart.delete()


class CartItem(models.Model):
    """
    Cart item model representing a product in a cart.
    """
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("cart")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("product")
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("variant")
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_("quantity")
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("added at")
    )
    
    class Meta:
        verbose_name = _("cart item")
        verbose_name_plural = _("cart items")
        unique_together = [["cart", "product", "variant"]]
        ordering = ["-added_at"]
    
    def __str__(self):
        if self.variant:
            return f"{self.quantity}x {self.product.name} ({self.variant.name})"
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def unit_price(self):
        """Get the unit price (variant price if applicable)."""
        if self.variant:
            return self.variant.final_price
        return self.product.price
    
    @property
    def subtotal(self):
        """Calculate item subtotal."""
        return self.unit_price * self.quantity
    
    def update_quantity(self, quantity):
        """Update item quantity."""
        if quantity < 1:
            self.delete()
        else:
            self.quantity = quantity
            self.save()


class Order(TimeStampedModel):
    """
    Order model representing a completed purchase.
    
    Features:
    - Unique order number generation
    - Full order lifecycle (Pending -> Paid -> Processing -> Shipped -> Delivered)
    - Shipping and billing address snapshots
    - Order total calculations
    """
    
    # Order identification
    order_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name=_("order number")
    )
    
    # User information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("user")
    )
    email = models.EmailField(
        verbose_name=_("email")
    )
    
    # Order status
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
        verbose_name=_("status")
    )
    
    # Shipping Address (snapshot)
    shipping_full_name = models.CharField(
        max_length=255,
        verbose_name=_("shipping full name")
    )
    shipping_street_address_1 = models.CharField(
        max_length=255,
        verbose_name=_("shipping street address 1")
    )
    shipping_street_address_2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("shipping street address 2")
    )
    shipping_city = models.CharField(
        max_length=100,
        verbose_name=_("shipping city")
    )
    shipping_state_province = models.CharField(
        max_length=100,
        verbose_name=_("shipping state/province")
    )
    shipping_postal_code = models.CharField(
        max_length=20,
        verbose_name=_("shipping postal code")
    )
    shipping_country = models.CharField(
        max_length=100,
        default="US",
        verbose_name=_("shipping country")
    )
    shipping_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("shipping phone")
    )
    
    # Billing Address (snapshot)
    billing_same_as_shipping = models.BooleanField(
        default=True,
        verbose_name=_("billing same as shipping")
    )
    billing_full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("billing full name")
    )
    billing_street_address_1 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("billing street address 1")
    )
    billing_street_address_2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("billing street address 2")
    )
    billing_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("billing city")
    )
    billing_state_province = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("billing state/province")
    )
    billing_postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("billing postal code")
    )
    billing_country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("billing country")
    )
    
    # Financial
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("subtotal")
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("shipping cost")
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("tax amount")
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("discount amount")
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("total")
    )
    
    # Currency
    currency = models.CharField(
        max_length=3,
        default="USD",
        verbose_name=_("currency")
    )
    
    # Notes
    customer_note = models.TextField(
        blank=True,
        verbose_name=_("customer note")
    )
    staff_note = models.TextField(
        blank=True,
        verbose_name=_("staff note")
    )
    
    # Tracking
    tracking_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("tracking number")
    )
    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("shipped at")
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("delivered at")
    )
    
    # IP Address for fraud detection
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP address")
    )
    
    # User agent for fraud detection
    user_agent = models.TextField(
        blank=True,
        verbose_name=_("user agent")
    )
    
    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order_number", "status"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["email", "status"]),
            models.Index(fields=["created_at"]),
        ]
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        """Generate order number if not set."""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate a unique order number."""
        # Format: ORD-YYYYMMDD-XXXXXX (where X is random)
        from datetime import datetime
        
        date_str = datetime.now().strftime("%Y%m%d")
        random_suffix = uuid.uuid4().hex[:6].upper()
        return f"ORD-{date_str}-{random_suffix}"
    
    def get_absolute_url(self):
        """Return the order detail URL."""
        return reverse("orders:order_detail", kwargs={"order_number": self.order_number})
    
    @property
    def item_count(self):
        """Return total number of items in order."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def is_paid(self):
        """Check if order is paid."""
        return self.status in [
            OrderStatus.PAID,
            OrderStatus.PROCESSING,
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED,
        ]
    
    @property
    def is_shipped(self):
        """Check if order is shipped."""
        return self.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]
    
    @property
    def is_delivered(self):
        """Check if order is delivered."""
        return self.status == OrderStatus.DELIVERED
    
    @property
    def is_cancelled(self):
        """Check if order is cancelled."""
        return self.status == OrderStatus.CANCELLED
    
    @property
    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status in [OrderStatus.PENDING, OrderStatus.PAID]
    
    @property
    def shipping_address_display(self):
        """Return formatted shipping address."""
        lines = [
            self.shipping_full_name,
            self.shipping_street_address_1,
        ]
        if self.shipping_street_address_2:
            lines.append(self.shipping_street_address_2)
        lines.append(f"{self.shipping_city}, {self.shipping_state_province} {self.shipping_postal_code}")
        lines.append(self.shipping_country)
        return "\n".join(lines)
    
    @property
    def billing_address_display(self):
        """Return formatted billing address."""
        if self.billing_same_as_shipping:
            return self.shipping_address_display
        
        lines = [
            self.billing_full_name,
            self.billing_street_address_1,
        ]
        if self.billing_street_address_2:
            lines.append(self.billing_street_address_2)
        lines.append(f"{self.billing_city}, {self.billing_state_province} {self.billing_postal_code}")
        lines.append(self.billing_country)
        return "\n".join(lines)
    
    def mark_as_paid(self):
        """Mark order as paid."""
        from django.utils import timezone
        self.status = OrderStatus.PAID
        self.save(update_fields=["status", "updated_at"])
    
    def mark_as_processing(self):
        """Mark order as processing."""
        self.status = OrderStatus.PROCESSING
        self.save(update_fields=["status", "updated_at"])
    
    def mark_as_shipped(self, tracking_number=""):
        """Mark order as shipped."""
        from django.utils import timezone
        self.status = OrderStatus.SHIPPED
        self.tracking_number = tracking_number
        self.shipped_at = timezone.now()
        self.save(update_fields=["status", "tracking_number", "shipped_at", "updated_at"])
    
    def mark_as_delivered(self):
        """Mark order as delivered."""
        from django.utils import timezone
        self.status = OrderStatus.DELIVERED
        self.delivered_at = timezone.now()
        self.save(update_fields=["status", "delivered_at", "updated_at"])
    
    def cancel(self):
        """Cancel the order and restore inventory."""
        if self.can_be_cancelled:
            self.status = OrderStatus.CANCELLED
            self.save(update_fields=["status", "updated_at"])
            # Restore inventory
            for item in self.items.all():
                item.product.increase_stock(item.quantity)


class OrderItem(models.Model):
    """
    Order item model representing a product in an order.
    
    Snapshots product information at time of purchase to preserve
    historical accuracy even if product details change later.
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("order")
    )
    
    # Product reference (for linking, but not dependent)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("product")
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("variant")
    )
    
    # Snapshot data (preserved even if product changes)
    product_name = models.CharField(
        max_length=255,
        verbose_name=_("product name")
    )
    product_sku = models.CharField(
        max_length=100,
        verbose_name=_("product SKU")
    )
    variant_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("variant name")
    )
    
    # Pricing snapshot
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("unit price")
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("quantity")
    )
    
    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")
        ordering = ["id"]
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name}"
    
    @property
    def subtotal(self):
        """Calculate item subtotal."""
        return self.unit_price * self.quantity
