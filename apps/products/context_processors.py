"""
Products Context Processors
Global context variables for templates.
"""

from .models import Category


def categories(request):
    """
    Add active categories to all template contexts.
    
    Returns:
        dict with 'categories' key containing all active root categories.
    """
    return {
        "categories": Category.objects.filter(
            is_active=True,
            is_deleted=False,
            parent=None
        ).prefetch_related("children")
    }
