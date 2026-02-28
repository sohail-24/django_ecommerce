"""
Accounts Decorators
Role-based permission decorators.
"""

from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def role_required(allowed_roles):
    """
    Decorator to check if user has one of the allowed roles.
    
    Args:
        allowed_roles: List or tuple of role strings (e.g., ['admin', 'staff'])
    
    Usage:
        @role_required(['admin', 'staff'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            
            if request.user.role not in allowed_roles and not request.user.is_superuser:
                raise PermissionDenied("You don't have permission to access this page.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Decorator to require admin role."""
    return role_required(["admin"])(view_func)


def staff_required(view_func):
    """Decorator to require staff or admin role."""
    return role_required(["admin", "staff"])(view_func)


def customer_required(view_func):
    """Decorator to require customer role."""
    return role_required(["customer"])(view_func)
