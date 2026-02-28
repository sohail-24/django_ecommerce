"""
Accounts Forms
Authentication and user management forms.
"""

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Address, User, UserProfile


class UserLoginForm(AuthenticationForm):
    """Custom login form with styling."""
    
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Email address"),
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Password"),
            }
        )
    )


class UserRegistrationForm(UserCreationForm):
    """Custom user registration form."""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("First name"),
            }
        ),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Last name"),
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Email address"),
            }
        ),
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Password"),
            }
        ),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Confirm password"),
            }
        ),
    )
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password1", "password2"]
    
    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("A user with this email already exists."))
        return email.lower()
    
    def save(self, commit=True):
        """Save the user with customer role."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.role = "customer"
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
        
        return user


class UserUpdateForm(forms.ModelForm):
    """Form for updating user information."""
    
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number"]


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""
    
    bio = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        ),
    )
    newsletter_subscribed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    sms_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    
    class Meta:
        model = UserProfile
        fields = ["avatar", "bio", "birth_date", "newsletter_subscribed", "sms_notifications"]


class AddressForm(forms.ModelForm):
    """Form for creating and editing addresses."""
    
    full_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Full name")}
        ),
    )
    street_address_1 = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Street address")}
        ),
    )
    street_address_2 = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Apartment, suite, unit, etc. (optional)"),
            }
        ),
    )
    city = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("City")}
        ),
    )
    state_province = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("State/Province")}
        ),
    )
    postal_code = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Postal code")}
        ),
    )
    country = forms.CharField(
        initial="US",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Country")}
        ),
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Phone number")}
        ),
    )
    is_default = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    
    class Meta:
        model = Address
        fields = [
            "address_type",
            "full_name",
            "street_address_1",
            "street_address_2",
            "city",
            "state_province",
            "postal_code",
            "country",
            "phone_number",
            "is_default",
        ]
        widgets = {
            "address_type": forms.Select(attrs={"class": "form-select"}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with styling."""
    
    old_password = forms.CharField(
        label=_("Current Password"),
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with styling."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter your email address"),
            }
        ),
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with styling."""
    
    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
