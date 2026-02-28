"""
Orders Admin Configuration
Admin interface for Order and OrderItem models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Cart, CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    
    model = OrderItem
    extra = 0
    readonly_fields = ["subtotal_display"]
    fields = [
        "product",
        "product_name",
        "product_sku",
        "variant_name",
        "unit_price",
        "quantity",
        "subtotal_display",
    ]
    
    def subtotal_display(self, obj):
        """Display item subtotal."""
        return f"${obj.subtotal:.2f}"
    subtotal_display.short_description = _("Subtotal")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order admin configuration."""
    
    list_display = [
        "order_number",
        "user",
        "email",
        "status",
        "total_display",
        "item_count",
        "created_at",
    ]
    list_filter = [
        "status",
        "created_at",
        "currency",
    ]
    search_fields = [
        "order_number",
        "email",
        "user__email",
        "shipping_full_name",
    ]
    readonly_fields = [
        "order_number",
        "created_at",
        "updated_at",
        "subtotal",
        "total",
        "item_count",
    ]
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    
    fieldsets = (
        (None, {
            "fields": (
                "order_number",
                "user",
                "email",
                "status",
            )
        }),
        (_("Shipping Address"), {
            "fields": (
                "shipping_full_name",
                "shipping_street_address_1",
                "shipping_street_address_2",
                "shipping_city",
                "shipping_state_province",
                "shipping_postal_code",
                "shipping_country",
                "shipping_phone",
            )
        }),
        (_("Billing Address"), {
            "fields": (
                "billing_same_as_shipping",
                "billing_full_name",
                "billing_street_address_1",
                "billing_street_address_2",
                "billing_city",
                "billing_state_province",
                "billing_postal_code",
                "billing_country",
            )
        }),
        (_("Financial"), {
            "fields": (
                "subtotal",
                "shipping_cost",
                "tax_amount",
                "discount_amount",
                "total",
                "currency",
            )
        }),
        (_("Notes"), {
            "fields": (
                "customer_note",
                "staff_note",
            )
        }),
        (_("Tracking"), {
            "fields": (
                "tracking_number",
                "shipped_at",
                "delivered_at",
            )
        }),
        (_("Metadata"), {
            "fields": (
                "ip_address",
                "user_agent",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",)
        }),
    )
    
    actions = [
        "mark_as_paid",
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_delivered",
        "cancel_orders",
    ]
    
    def total_display(self, obj):
        """Display order total with currency."""
        return f"${obj.total:.2f}"
    total_display.short_description = _("Total")
    
    @admin.action(description=_("Mark selected orders as paid"))
    def mark_as_paid(self, request, queryset):
        """Bulk mark orders as paid."""
        for order in queryset:
            order.mark_as_paid()
    
    @admin.action(description=_("Mark selected orders as processing"))
    def mark_as_processing(self, request, queryset):
        """Bulk mark orders as processing."""
        queryset.update(status="processing")
    
    @admin.action(description=_("Mark selected orders as shipped"))
    def mark_as_shipped(self, request, queryset):
        """Bulk mark orders as shipped."""
        for order in queryset:
            order.mark_as_shipped()
    
    @admin.action(description=_("Mark selected orders as delivered"))
    def mark_as_delivered(self, request, queryset):
        """Bulk mark orders as delivered."""
        for order in queryset:
            order.mark_as_delivered()
    
    @admin.action(description=_("Cancel selected orders"))
    def cancel_orders(self, request, queryset):
        """Bulk cancel orders."""
        for order in queryset:
            order.cancel()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Order item admin configuration."""
    
    list_display = [
        "order",
        "product_name",
        "product_sku",
        "unit_price",
        "quantity",
        "subtotal",
    ]
    list_filter = ["order__status"]
    search_fields = ["product_name", "product_sku", "order__order_number"]
    raw_id_fields = ["order", "product", "variant"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Cart admin configuration."""
    
    list_display = [
        "id",
        "user",
        "session_key_short",
        "item_count",
        "total",
        "created_at",
    ]
    search_fields = ["user__email", "session_key"]
    
    def session_key_short(self, obj):
        """Display shortened session key."""
        if obj.session_key:
            return obj.session_key[:20] + "..."
        return "-"
    session_key_short.short_description = _("Session Key")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Cart item admin configuration."""
    
    list_display = [
        "cart",
        "product",
        "variant",
        "quantity",
        "subtotal",
    ]
    list_filter = ["cart__user"]
    search_fields = ["product__name", "cart__user__email"]
    raw_id_fields = ["cart", "product", "variant"]
