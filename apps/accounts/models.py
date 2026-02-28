"""
Accounts Models
Custom User model with role-based access control.
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class UserRole(models.TextChoices):
    """User role choices for RBAC."""
    
    ADMIN = "admin", _("Administrator")
    STAFF = "staff", _("Staff")
    CUSTOMER = "customer", _("Customer")


class UserManager(BaseUserManager):
    """Custom user manager for the User model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError(_("Users must have an email address"))
        
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_active", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        
        return self.create_user(email, password, **extra_fields)
    
    def customers(self):
        """Return only customer users."""
        return self.filter(role=UserRole.CUSTOMER)
    
    def staff(self):
        """Return only staff users."""
        return self.filter(role__in=[UserRole.STAFF, UserRole.ADMIN])


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom User model with email as the primary identifier.
    
    Features:
    - Email-based authentication
    - Role-based access control (RBAC)
    - Phone number validation
    - Soft delete support via is_active
    """
    
    # Primary identifier
    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name=_("email address"),
        help_text=_("Primary email address used for login")
    )
    
    # Personal Information
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("first name")
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("last name")
    )
    
    # Phone validation
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        verbose_name=_("phone number")
    )
    
    # Role-based access control
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        db_index=True,
        verbose_name=_("role"),
        help_text=_("User's role determines their permissions")
    )
    
    # Status fields
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("active"),
        help_text=_("Designates whether this user should be treated as active.")
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("staff status"),
        help_text=_("Designates whether the user can log into the admin site.")
    )
    
    # Email verification
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_("email verified"),
        help_text=_("Designates whether the user's email is verified.")
    )
    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("email verified at")
    )
    
    # Important dates
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("date joined")
    )
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("last login")
    )
    
    # Configuration
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["role", "is_active"]),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the user's full name."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email
    
    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name or self.email
    
    @property
    def is_admin(self):
        """Check if user is an administrator."""
        return self.role == UserRole.ADMIN or self.is_superuser
    
    @property
    def is_staff_user(self):
        """Check if user is staff (including admin)."""
        return self.role in [UserRole.STAFF, UserRole.ADMIN]
    
    @property
    def is_customer(self):
        """Check if user is a customer."""
        return self.role == UserRole.CUSTOMER
    
    def verify_email(self):
        """Mark the user's email as verified."""
        self.email_verified = True
        self.email_verified_at = timezone.now()
        self.save(update_fields=["email_verified", "email_verified_at"])
    
    def has_perm(self, perm, obj=None):
        """Check if user has a specific permission."""
        # Admin has all permissions
        if self.is_admin:
            return True
        return super().has_perm(perm, obj)
    
    def has_module_perms(self, app_label):
        """Check if user has permissions for a specific app."""
        # Admin has all permissions
        if self.is_admin:
            return True
        return super().has_module_perms(app_label)


class UserProfile(TimeStampedModel):
    """
    Extended user profile information.
    Separated from User for better organization and future extensibility.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("user")
    )
    
    # Profile image
    avatar = models.ImageField(
        upload_to="avatars/%Y/%m/",
        blank=True,
        null=True,
        verbose_name=_("avatar")
    )
    
    # Bio
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_("bio")
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("birth date")
    )
    
    # Preferences
    newsletter_subscribed = models.BooleanField(
        default=True,
        verbose_name=_("newsletter subscribed")
    )
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name=_("SMS notifications")
    )
    
    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")
    
    def __str__(self):
        return f"{self.user.email}'s Profile"


class Address(TimeStampedModel):
    """
    User address model for shipping and billing.
    Supports multiple addresses per user.
    """
    
    class AddressType(models.TextChoices):
        SHIPPING = "shipping", _("Shipping")
        BILLING = "billing", _("Billing")
        BOTH = "both", _("Both")
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("user")
    )
    
    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.SHIPPING,
        verbose_name=_("address type")
    )
    
    # Address fields
    full_name = models.CharField(
        max_length=255,
        verbose_name=_("full name")
    )
    street_address_1 = models.CharField(
        max_length=255,
        verbose_name=_("street address 1")
    )
    street_address_2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("street address 2")
    )
    city = models.CharField(
        max_length=100,
        verbose_name=_("city")
    )
    state_province = models.CharField(
        max_length=100,
        verbose_name=_("state/province")
    )
    postal_code = models.CharField(
        max_length=20,
        verbose_name=_("postal code")
    )
    country = models.CharField(
        max_length=100,
        default="US",
        verbose_name=_("country")
    )
    
    # Contact at address
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        verbose_name=_("phone number")
    )
    
    # Default address flag
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("default address")
    )
    
    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
        ordering = ["-is_default", "-created_at"]
    
    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.state_province}"
    
    def save(self, *args, **kwargs):
        """Ensure only one default address per type per user."""
        if self.is_default:
            # Clear other default addresses of the same type
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    @property
    def full_address(self):
        """Return the full formatted address."""
        parts = [
            self.street_address_1,
            self.street_address_2,
            f"{self.city}, {self.state_province} {self.postal_code}",
            self.country
        ]
        return ", ".join(filter(None, parts))
