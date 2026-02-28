"""
Products Admin Configuration
Admin interface for Category, Product, and related models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Category, Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""
    
    model = ProductImage
    extra = 1
    fields = ["image", "alt_text", "is_primary", "order"]


class ProductVariantInline(admin.TabularInline):
    """Inline admin for product variants."""
    
    model = ProductVariant
    extra = 1
    fields = ["name", "sku", "size", "color", "price_adjustment", "stock_quantity", "is_active"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin configuration."""
    
    list_display = [
        "name",
        "slug",
        "parent",
        "product_count",
        "is_active",
        "order",
    ]
    list_filter = ["is_active", "parent"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["order", "is_active"]
    
    fieldsets = (
        (None, {
            "fields": ("name", "slug", "parent", "description")
        }),
        (_("Media"), {
            "fields": ("image",)
        }),
        (_("Settings"), {
            "fields": ("is_active", "order")
        }),
        (_("SEO"), {
            "fields": ("meta_title", "meta_description"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product admin configuration."""
    
    list_display = [
        "name",
        "sku",
        "category",
        "price",
        "stock_quantity",
        "status",
        "is_active",
        "is_featured",
        "created_at",
    ]
    list_filter = [
        "status",
        "is_active",
        "is_featured",
        "category",
        "created_at",
    ]
    search_fields = [
        "name",
        "sku",
        "description",
        "short_description",
    ]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["status", "is_active", "is_featured", "price"]
    date_hierarchy = "created_at"
    
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        (None, {
            "fields": (
                "name",
                "slug",
                "sku",
                "category",
                "description",
                "short_description",
            )
        }),
        (_("Pricing"), {
            "fields": (
                "price",
                "compare_at_price",
                "cost_price",
            )
        }),
        (_("Inventory"), {
            "fields": (
                "stock_quantity",
                "low_stock_threshold",
                "track_inventory",
                "allow_backorders",
            )
        }),
        (_("Status"), {
            "fields": (
                "status",
                "is_active",
                "is_featured",
            )
        }),
        (_("Physical Attributes"), {
            "fields": ("weight",),
            "classes": ("collapse",)
        }),
        (_("SEO"), {
            "fields": ("meta_title", "meta_description"),
            "classes": ("collapse",)
        }),
    )
    
    actions = [
        "make_active",
        "make_inactive",
        "make_featured",
        "remove_featured",
    ]
    
    @admin.action(description=_("Activate selected products"))
    def make_active(self, request, queryset):
        """Bulk activate products."""
        queryset.update(is_active=True)
    
    @admin.action(description=_("Deactivate selected products"))
    def make_inactive(self, request, queryset):
        """Bulk deactivate products."""
        queryset.update(is_active=False)
    
    @admin.action(description=_("Mark as featured"))
    def make_featured(self, request, queryset):
        """Bulk mark products as featured."""
        queryset.update(is_featured=True)
    
    @admin.action(description=_("Remove from featured"))
    def remove_featured(self, request, queryset):
        """Bulk remove products from featured."""
        queryset.update(is_featured=False)
    
    def get_queryset(self, request):
        """Include soft-deleted products in admin."""
        return Product.objects.all()


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Product image admin configuration."""
    
    list_display = [
        "product",
        "image_preview",
        "is_primary",
        "order",
    ]
    list_filter = ["is_primary"]
    search_fields = ["product__name", "alt_text"]
    list_editable = ["is_primary", "order"]
    
    def image_preview(self, obj):
        """Display image preview in admin."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.image.url
            )
        return _("No image")
    image_preview.short_description = _("Preview")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Product variant admin configuration."""
    
    list_display = [
        "product",
        "name",
        "sku",
        "size",
        "color",
        "final_price",
        "stock_quantity",
        "is_active",
    ]
    list_filter = ["is_active", "size", "color"]
    search_fields = ["product__name", "name", "sku"]
    list_editable = ["is_active", "stock_quantity"]
