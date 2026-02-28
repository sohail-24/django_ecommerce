"""
Products Models
Category and Product models with inventory tracking and soft delete.
"""

from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class Category(BaseModel):
    """
    Product category model.
    Supports hierarchical categories with parent-child relationships.
    """
    
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("name")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name=_("slug")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description")
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("parent category")
    )
    image = models.ImageField(
        upload_to="categories/%Y/%m/",
        blank=True,
        null=True,
        verbose_name=_("image")
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("active")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order")
    )
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("meta title")
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name=_("meta description")
    )
    
    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["order", "name"]
        indexes = [
            models.Index(fields=["slug", "is_active"]),
            models.Index(fields=["parent", "is_active"]),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return the category detail URL."""
        return reverse("products:category_detail", kwargs={"slug": self.slug})
    
    @property
    def product_count(self):
        """Return the number of active products in this category."""
        return self.products.filter(is_active=True, is_deleted=False).count()
    
    def get_full_path(self):
        """Return the full category path (parent > child)."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Product(BaseModel):
    """
    Product model with inventory tracking and soft delete.
    
    Features:
    - SKU (Stock Keeping Unit) for inventory management
    - Multiple images support
    - Inventory tracking with low stock alerts
    - Slug-based URLs for SEO
    - Soft delete support
    """
    
    class ProductStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ACTIVE = "active", _("Active")
        OUT_OF_STOCK = "out_of_stock", _("Out of Stock")
        DISCONTINUED = "discontinued", _("Discontinued")
    
    # Basic Information
    name = models.CharField(
        max_length=255,
        verbose_name=_("name")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name=_("slug")
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name=_("SKU"),
        help_text=_("Stock Keeping Unit - unique product identifier")
    )
    description = models.TextField(
        verbose_name=_("description")
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("short description")
    )
    
    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("category")
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("price")
    )
    compare_at_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("compare at price"),
        help_text=_("Original price for display when on sale")
    )
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("cost price"),
        help_text=_("Internal cost for margin calculations")
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("stock quantity")
    )
    low_stock_threshold = models.PositiveIntegerField(
        default=10,
        verbose_name=_("low stock threshold"),
        help_text=_("Alert when stock falls below this number")
    )
    track_inventory = models.BooleanField(
        default=True,
        verbose_name=_("track inventory")
    )
    allow_backorders = models.BooleanField(
        default=False,
        verbose_name=_("allow backorders")
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
        db_index=True,
        verbose_name=_("status")
    )
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("active")
    )
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("featured")
    )
    
    # Physical Attributes (for clothing)
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("weight (kg)")
    )
    
    # SEO
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("meta title")
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name=_("meta description")
    )
    
    # Statistics
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("view count")
    )
    
    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug", "is_active", "is_deleted"]),
            models.Index(fields=["category", "is_active", "is_deleted"]),
            models.Index(fields=["status", "is_active"]),
            models.Index(fields=["is_featured", "is_active"]),
            models.Index(fields=["price"]),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Update status based on stock
        if self.track_inventory and self.status == self.ProductStatus.ACTIVE:
            if self.stock_quantity <= 0 and not self.allow_backorders:
                self.status = self.ProductStatus.OUT_OF_STOCK
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return the product detail URL."""
        return reverse("products:product_detail", kwargs={"slug": self.slug})
    
    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorders
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock."""
        if not self.track_inventory:
            return False
        return 0 < self.stock_quantity <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale."""
        if self.compare_at_price and self.compare_at_price > self.price:
            discount = ((self.compare_at_price - self.price) / self.compare_at_price) * 100
            return round(discount)
        return 0
    
    @property
    def is_on_sale(self):
        """Check if product is on sale."""
        return self.compare_at_price and self.compare_at_price > self.price
    
    @property
    def primary_image(self):
        """Return the primary product image."""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()
    
    def decrease_stock(self, quantity):
        """Decrease stock quantity by given amount."""
        if self.track_inventory:
            self.stock_quantity = max(0, self.stock_quantity - quantity)
            self.save(update_fields=["stock_quantity"])
    
    def increase_stock(self, quantity):
        """Increase stock quantity by given amount."""
        if self.track_inventory:
            self.stock_quantity += quantity
            self.save(update_fields=["stock_quantity"])
    
    def increment_view_count(self):
        """Increment the product view count."""
        self.view_count += 1
        self.save(update_fields=["view_count"])


class ProductImage(BaseModel):
    """
    Product image model.
    Supports multiple images per product with primary image designation.
    """
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("product")
    )
    image = models.ImageField(
        upload_to="products/%Y/%m/",
        verbose_name=_("image")
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("alt text"),
        help_text=_("Alternative text for accessibility and SEO")
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("primary image")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order")
    )
    
    class Meta:
        verbose_name = _("product image")
        verbose_name_plural = _("product images")
        ordering = ["order", "created_at"]
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary image per product."""
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(BaseModel):
    """
    Product variant model for size/color options.
    Allows products to have multiple variants (e.g., Small Red, Large Blue).
    """
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name=_("product")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("variant name"),
        help_text=_("e.g., 'Small - Red'")
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("SKU")
    )
    price_adjustment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("price adjustment"),
        help_text=_("Amount to add/subtract from base price")
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("stock quantity")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("active")
    )
    
    # Variant attributes
    size = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("size")
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("color")
    )
    material = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("material")
    )
    
    class Meta:
        verbose_name = _("product variant")
        verbose_name_plural = _("product variants")
        ordering = ["name"]
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def final_price(self):
        """Calculate final price including adjustment."""
        return self.product.price + self.price_adjustment
    
    @property
    def is_in_stock(self):
        """Check if variant is in stock."""
        return self.stock_quantity > 0
