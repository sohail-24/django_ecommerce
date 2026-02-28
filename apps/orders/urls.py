"""
Orders URL Configuration
Cart and checkout URLs.
"""

from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    # Cart
    path(
        "cart/",
        views.CartDetailView.as_view(),
        name="cart_detail"
    ),
    path(
        "cart/add/<slug:product_slug>/",
        views.CartAddView.as_view(),
        name="cart_add"
    ),
    path(
        "cart/remove/<int:item_id>/",
        views.CartRemoveView.as_view(),
        name="cart_remove"
    ),
    path(
        "cart/update/<int:item_id>/",
        views.CartUpdateView.as_view(),
        name="cart_update"
    ),
    path(
        "cart/clear/",
        views.CartClearView.as_view(),
        name="cart_clear"
    ),
    
    # Checkout
    path(
        "checkout/",
        views.CheckoutView.as_view(),
        name="checkout"
    ),
    path(
        "checkout/success/<str:order_number>/",
        views.CheckoutSuccessView.as_view(),
        name="checkout_success"
    ),
    
    # Order Detail
    path(
        "order/<str:order_number>/",
        views.OrderDetailView.as_view(),
        name="order_detail"
    ),
]
