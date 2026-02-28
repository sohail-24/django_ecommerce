"""
Accounts Admin Configuration
Admin interface for User, UserProfile, and Address models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Address, User, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profile."""
    
    model = UserProfile
    can_delete = False
    verbose_name_plural = _("Profile")
    fk_name = "user"


class AddressInline(admin.TabularInline):
    """Inline admin for user addresses."""
    
    model = Address
    extra = 0
    verbose_name_plural = _("Addresses")
    fields = ["address_type", "full_name", "city", "state_province", "is_default"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with role-based display."""
    
    inlines = [UserProfileInline, AddressInline]
    
    list_display = [
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "email_verified",
        "date_joined",
    ]
    list_filter = [
        "role",
        "is_active",
        "is_staff",
        "email_verified",
        "date_joined",
    ]
    search_fields = ["email", "first_name", "last_name", "phone_number"]
    ordering = ["-date_joined"]
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "phone_number")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Email verification"),
            {"fields": ("email_verified", "email_verified_at")},
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    
    readonly_fields = ["date_joined", "last_login", "email_verified_at"]
    
    actions = ["make_active", "make_inactive", "verify_emails"]
    
    @admin.action(description=_("Activate selected users"))
    def make_active(self, request, queryset):
        """Bulk activate users."""
        queryset.update(is_active=True)
    
    @admin.action(description=_("Deactivate selected users"))
    def make_inactive(self, request, queryset):
        """Bulk deactivate users."""
        queryset.update(is_active=False)
    
    @admin.action(description=_("Mark emails as verified"))
    def verify_emails(self, request, queryset):
        """Bulk verify user emails."""
        from django.utils import timezone
        queryset.update(email_verified=True, email_verified_at=timezone.now())


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Address admin configuration."""
    
    list_display = [
        "user",
        "full_name",
        "address_type",
        "city",
        "state_province",
        "country",
        "is_default",
    ]
    list_filter = ["address_type", "country", "is_default", "created_at"]
    search_fields = ["user__email", "full_name", "city", "postal_code"]
    raw_id_fields = ["user"]
