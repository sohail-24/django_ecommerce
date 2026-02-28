"""
Accounts Tests
Unit tests for accounts models and views.
"""

from django.test import TestCase
from django.urls import reverse

from .models import Address, User, UserProfile


class UserModelTests(TestCase):
    """Tests for the User model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
    
    def test_user_creation(self):
        """Test user is created correctly."""
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.get_full_name(), "Test User")
        self.assertTrue(self.user.check_password("testpassword123"))
        self.assertEqual(self.user.role, "customer")
    
    def test_user_is_customer(self):
        """Test user is identified as customer."""
        self.assertTrue(self.user.is_customer)
        self.assertFalse(self.user.is_staff_user)
        self.assertFalse(self.user.is_admin)
    
    def test_superuser_creation(self):
        """Test superuser is created correctly."""
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword123"
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.role, "admin")


class AddressModelTests(TestCase):
    """Tests for the Address model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123"
        )
        self.address = Address.objects.create(
            user=self.user,
            full_name="Test User",
            street_address_1="123 Test St",
            city="Test City",
            state_province="CA",
            postal_code="12345",
            country="US",
            is_default=True
        )
    
    def test_address_creation(self):
        """Test address is created correctly."""
        self.assertEqual(self.address.full_name, "Test User")
        self.assertEqual(self.address.city, "Test City")
        self.assertTrue(self.address.is_default)
    
    def test_full_address_property(self):
        """Test full address formatting."""
        expected = "123 Test St, Test City, CA 12345, US"
        self.assertEqual(self.address.full_address, expected)


class AuthenticationViewTests(TestCase):
    """Tests for authentication views."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
    
    def test_login_view(self):
        """Test login view is accessible."""
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
    
    def test_register_view(self):
        """Test register view is accessible."""
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "test@example.com", "password": "testpassword123"}
        )
        self.assertEqual(response.status_code, 302)
