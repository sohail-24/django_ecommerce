"""
Orders Forms
Forms for cart and checkout processes.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Address


class AddToCartForm(forms.Form):
    """Form for adding products to cart."""
    
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": 1,
            }
        ),
    )
    variant_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(),
    )


class CartUpdateForm(forms.Form):
    """Form for updating cart item quantities."""
    
    quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control quantity-input",
                "min": 0,
            }
        ),
    )


class CheckoutAddressForm(forms.Form):
    """Form for checkout address selection."""
    
    address_id = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=False,
        empty_label=_("Select an address..."),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    use_new_address = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    
    # New address fields
    shipping_full_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Full name"),
            }
        ),
    )
    shipping_street_address_1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Street address"),
            }
        ),
    )
    shipping_street_address_2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Apartment, suite, etc. (optional)"),
            }
        ),
    )
    shipping_city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("City"),
            }
        ),
    )
    shipping_state_province = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("State/Province"),
            }
        ),
    )
    shipping_postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Postal code"),
            }
        ),
    )
    shipping_country = forms.CharField(
        max_length=100,
        initial="US",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Country"),
            }
        ),
    )
    shipping_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Phone number"),
            }
        ),
    )
    
    customer_note = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": _("Any special instructions for your order..."),
            }
        ),
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["address_id"].queryset = user.addresses.all()
    
    def clean(self):
        cleaned_data = super().clean()
        use_new_address = cleaned_data.get("use_new_address")
        address_id = cleaned_data.get("address_id")
        
        if not address_id and not use_new_address:
            raise forms.ValidationError(
                _("Please select an existing address or enter a new one.")
            )
        
        if use_new_address:
            required_fields = [
                "shipping_full_name",
                "shipping_street_address_1",
                "shipping_city",
                "shipping_state_province",
                "shipping_postal_code",
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(
                        field,
                        forms.ValidationError(_("This field is required."))
                    )
        
        return cleaned_data
