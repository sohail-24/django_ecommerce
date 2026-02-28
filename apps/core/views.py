"""
Core Views
Health check and home page views.
"""

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView


class HealthCheckView(View):
    """
    Health check endpoint for load balancers and monitoring.
    
    Returns:
        200 OK if database connection is healthy
        503 Service Unavailable if database is down
    """
    
    def get(self, request, *args, **kwargs):
        health_status = {
            "status": "healthy",
            "service": "django-ecommerce",
            "version": "1.0.0",
            "checks": {
                "database": "unknown",
            },
        }
        status_code = 200
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            health_status["checks"]["database"] = "healthy"
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["checks"]["database"] = f"unhealthy: {str(e)}"
            status_code = 503
        
        return JsonResponse(health_status, status=status_code)


class HomeView(TemplateView):
    """Home page view with featured products."""
    
    template_name = "core/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Import here to avoid circular imports
        from apps.products.models import Product
        
        context["featured_products"] = Product.objects.filter(
            is_active=True,
            is_featured=True
        ).select_related("category")[:8]
        
        context["new_arrivals"] = Product.objects.filter(
            is_active=True
        ).select_related("category").order_by("-created_at")[:4]
        
        return context


class AboutView(TemplateView):
    """About page view."""
    
    template_name = "core/about.html"


class ContactView(TemplateView):
    """Contact page view."""
    
    template_name = "core/contact.html"
