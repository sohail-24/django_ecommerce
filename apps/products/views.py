"""
Products Views
Product browsing, category filtering, and search functionality.
"""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Category, Product


class ProductListView(ListView):
    """List all active products with filtering and pagination."""
    
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12
    
    def get_queryset(self):
        """Return active, non-deleted products."""
        queryset = Product.objects.filter(
            is_active=True,
            is_deleted=False,
            status=Product.ProductStatus.ACTIVE
        ).select_related("category").prefetch_related("images")
        
        # Category filter
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Price filter
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sorting
        sort = self.request.GET.get("sort", "-created_at")
        sort_options = {
            "price_low": "price",
            "price_high": "-price",
            "name": "name",
            "newest": "-created_at",
            "popular": "-view_count",
        }
        queryset = queryset.order_by(sort_options.get(sort, "-created_at"))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(
            is_active=True,
            is_deleted=False
        )
        context["current_category"] = self.request.GET.get("category")
        context["current_sort"] = self.request.GET.get("sort", "newest")
        return context


class ProductDetailView(DetailView):
    """Display product details."""
    
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"
    
    def get_queryset(self):
        """Return active, non-deleted products."""
        return Product.objects.filter(
            is_active=True,
            is_deleted=False
        ).select_related("category").prefetch_related("images", "variants")
    
    def get_object(self, queryset=None):
        """Get product and increment view count."""
        obj = super().get_object(queryset)
        obj.increment_view_count()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Related products from same category
        context["related_products"] = Product.objects.filter(
            category=product.category,
            is_active=True,
            is_deleted=False
        ).exclude(pk=product.pk)[:4]
        
        # Recently viewed (from session)
        recently_viewed = self.request.session.get("recently_viewed", [])
        if product.pk not in recently_viewed:
            recently_viewed.insert(0, product.pk)
            recently_viewed = recently_viewed[:10]  # Keep last 10
            self.request.session["recently_viewed"] = recently_viewed
        
        return context


class CategoryDetailView(DetailView):
    """Display category with its products."""
    
    model = Category
    template_name = "products/category_detail.html"
    context_object_name = "category"
    slug_url_kwarg = "slug"
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True, is_deleted=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Get products in this category
        products = Product.objects.filter(
            category=category,
            is_active=True,
            is_deleted=False,
            status=Product.ProductStatus.ACTIVE
        ).select_related("category").prefetch_related("images")
        
        # Include products from child categories
        child_categories = category.children.filter(is_active=True)
        if child_categories.exists():
            products = products | Product.objects.filter(
                category__in=child_categories,
                is_active=True,
                is_deleted=False,
                status=Product.ProductStatus.ACTIVE
            )
        
        context["products"] = products.distinct()[:24]
        context["subcategories"] = child_categories
        
        return context


class ProductSearchView(ListView):
    """Search products by name, description, or SKU."""
    
    model = Product
    template_name = "products/product_search.html"
    context_object_name = "products"
    paginate_by = 12
    
    def get_queryset(self):
        """Search products based on query."""
        query = self.request.GET.get("q", "").strip()
        
        if not query:
            return Product.objects.none()
        
        return Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(sku__iexact=query) |
            Q(category__name__icontains=query)
        ).filter(
            is_active=True,
            is_deleted=False,
            status=Product.ProductStatus.ACTIVE
        ).select_related("category").prefetch_related("images")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["result_count"] = self.get_queryset().count()
        return context


class FeaturedProductsView(ListView):
    """Display featured products."""
    
    model = Product
    template_name = "products/featured_products.html"
    context_object_name = "products"
    paginate_by = 12
    
    def get_queryset(self):
        return Product.objects.filter(
            is_featured=True,
            is_active=True,
            is_deleted=False,
            status=Product.ProductStatus.ACTIVE
        ).select_related("category").prefetch_related("images")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Featured Products"
        return context
