"""
Payments URL Configuration
Payment processing and webhook URLs.
"""

from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    # Payment Processing
    path(
        "process/<str:order_number>/",
        views.PaymentProcessView.as_view(),
        name="process"
    ),
    path(
        "success/<str:order_number>/",
        views.PaymentSuccessView.as_view(),
        name="success"
    ),
    path(
        "cancel/<str:order_number>/",
        views.PaymentCancelView.as_view(),
        name="cancel"
    ),
    
    # Stripe Webhook
    path(
        "webhook/stripe/",
        views.StripeWebhookView.as_view(),
        name="stripe_webhook"
    ),
]
