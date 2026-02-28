"""
Products URL Configuration
Product and category browsing URLs.
"""

from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # Product List
    path(
        "",
        views.ProductListView.as_view(),
        name="product_list"
    ),

    # Category Detail
    path(
        "category/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail"
    ),

    # Search (STATIC routes first)
    path(
        "search/",
        views.ProductSearchView.as_view(),
        name="product_search"
    ),

    # Featured (STATIC routes before dynamic slug)
    path(
        "featured/",
        views.FeaturedProductsView.as_view(),
        name="featured_products"
    ),

    # Product Detail (DYNAMIC — ALWAYS LAST)
    path(
        "<slug:slug>/",
        views.ProductDetailView.as_view(),
        name="product_detail"
    ),
]