"""
Django E-commerce URL Configuration
Root URL router for the entire application.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.views import HealthCheckView, HomeView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # Core
    path("", HomeView.as_view(), name="home"),
    path("health/", HealthCheckView.as_view(), name="health_check"),
    
    # Apps
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("products/", include("apps.products.urls", namespace="products")),
    path("orders/", include("apps.orders.urls", namespace="orders")),
    path("payments/", include("apps.payments.urls", namespace="payments")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
