"""
Accounts Views
User authentication, registration, and profile management.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.orders.models import Order

from .forms import (
    AddressForm,
    UserProfileForm,
    UserRegistrationForm,
    UserUpdateForm,
)
from .models import Address, User, UserProfile


class CustomLoginView(LoginView):
    """Custom login view with styling."""
    
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to home after login."""
        return reverse_lazy("home")


class RegisterView(CreateView):
    """User registration view."""
    
    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("home")
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users to home."""
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Log in the user after successful registration."""
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            _("Welcome! Your account has been created successfully.")
        )
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view."""
    
    template_name = "accounts/profile.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["addresses"] = self.request.user.addresses.all()
        context["recent_orders"] = Order.objects.filter(
            user=self.request.user
        ).order_by("-created_at")[:5]
        return context


class ProfileEditView(LoginRequiredMixin, View):
    """View for editing user profile."""
    
    template_name = "accounts/profile_edit.html"
    
    def get(self, request, *args, **kwargs):
        user_form = UserUpdateForm(instance=request.user)
        
        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile_form = UserProfileForm(instance=profile)
        
        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
            }
        )
    
    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _("Your profile has been updated."))
            return redirect("accounts:profile")
        
        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
            }
        )


# =============================================================================
# ADDRESS VIEWS
# =============================================================================

class AddressListView(LoginRequiredMixin, ListView):
    """List all user addresses."""
    
    model = Address
    template_name = "accounts/address_list.html"
    context_object_name = "addresses"
    
    def get_queryset(self):
        return self.request.user.addresses.all()


class AddressCreateView(LoginRequiredMixin, CreateView):
    """Create a new address."""
    
    model = Address
    form_class = AddressForm
    template_name = "accounts/address_form.html"
    success_url = reverse_lazy("accounts:address_list")
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _("Address added successfully."))
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing address."""
    
    model = Address
    form_class = AddressForm
    template_name = "accounts/address_form.html"
    success_url = reverse_lazy("accounts:address_list")
    
    def get_queryset(self):
        return self.request.user.addresses.all()
    
    def form_valid(self, form):
        messages.success(self.request, _("Address updated successfully."))
        return super().form_valid(form)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """Delete an address."""
    
    model = Address
    template_name = "accounts/address_confirm_delete.html"
    success_url = reverse_lazy("accounts:address_list")
    
    def get_queryset(self):
        return self.request.user.addresses.all()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Address deleted successfully."))
        return super().delete(request, *args, **kwargs)


class AddressSetDefaultView(LoginRequiredMixin, View):
    """Set an address as default."""
    
    def post(self, request, pk, *args, **kwargs):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.is_default = True
        address.save()
        messages.success(request, _("Default address updated."))
        return redirect("accounts:address_list")


# =============================================================================
# ORDER HISTORY VIEW
# =============================================================================

class OrderHistoryView(LoginRequiredMixin, ListView):
    """View order history for the user."""
    
    model = Order
    template_name = "accounts/order_history.html"
    context_object_name = "orders"
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related("items", "items__product")
