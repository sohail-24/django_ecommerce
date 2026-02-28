"""
Payments Models
Payment model with transaction tracking and Stripe integration support.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel
from apps.orders.models import Order


class PaymentStatus(models.TextChoices):
    """Payment status choices."""
    
    PENDING = "pending", _("Pending")
    PROCESSING = "processing", _("Processing")
    COMPLETED = "completed", _("Completed")
    FAILED = "failed", _("Failed")
    REFUNDED = "refunded", _("Refunded")
    PARTIALLY_REFUNDED = "partially_refunded", _("Partially Refunded")
    CANCELLED = "cancelled", _("Cancelled")


class PaymentMethod(models.TextChoices):
    """Payment method choices."""
    
    CREDIT_CARD = "credit_card", _("Credit Card")
    DEBIT_CARD = "debit_card", _("Debit Card")
    PAYPAL = "paypal", _("PayPal")
    STRIPE = "stripe", _("Stripe")
    BANK_TRANSFER = "bank_transfer", _("Bank Transfer")
    CASH_ON_DELIVERY = "cash_on_delivery", _("Cash on Delivery")


class Payment(TimeStampedModel):
    """
    Payment model for tracking all payment transactions.
    
    Features:
    - Multiple payment methods support
    - Transaction ID tracking
    - Full refund support
    - Stripe integration ready
    - Payment status lifecycle
    """
    
    # Relationships
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name=_("order")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name=_("user")
    )
    
    # Payment Details
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("amount")
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        verbose_name=_("currency")
    )
    
    # Payment Method
    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.STRIPE,
        verbose_name=_("payment method")
    )
    
    # Status
    status = models.CharField(
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        verbose_name=_("status")
    )
    
    # Transaction IDs (for external payment providers)
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name=_("transaction ID"),
        help_text=_("External payment provider transaction ID")
    )
    payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name=_("payment intent ID"),
        help_text=_("Stripe Payment Intent ID")
    )
    charge_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("charge ID"),
        help_text=_("Stripe Charge ID")
    )
    
    # Card Information (masked for security)
    card_last_four = models.CharField(
        max_length=4,
        blank=True,
        verbose_name=_("card last four")
    )
    card_brand = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("card brand")
    )
    
    # Billing Information (snapshot)
    billing_email = models.EmailField(
        blank=True,
        verbose_name=_("billing email")
    )
    billing_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("billing name")
    )
    
    # Refund Information
    refunded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("refunded amount")
    )
    refund_reason = models.TextField(
        blank=True,
        verbose_name=_("refund reason")
    )
    
    # Error Information
    error_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("error code")
    )
    error_message = models.TextField(
        blank=True,
        verbose_name=_("error message")
    )
    
    # Metadata
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("description")
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("metadata"),
        help_text=_("Additional payment metadata from provider")
    )
    
    # IP Address for fraud detection
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP address")
    )
    
    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "status"]),
            models.Index(fields=["transaction_id"]),
            models.Index(fields=["payment_intent_id"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]
    
    def __str__(self):
        return f"Payment {self.id} - {self.order.order_number} - {self.status}"
    
    @property
    def is_successful(self):
        """Check if payment was successful."""
        return self.status == PaymentStatus.COMPLETED
    
    @property
    def is_refundable(self):
        """Check if payment can be refunded."""
        return self.status == PaymentStatus.COMPLETED and self.refundable_amount > 0
    
    @property
    def refundable_amount(self):
        """Calculate refundable amount."""
        return self.amount - self.refunded_amount
    
    @property
    def display_amount(self):
        """Return formatted amount with currency."""
        return f"${self.amount:.2f}"
    
    def mark_as_completed(self, transaction_id="", payment_intent_id="", charge_id=""):
        """Mark payment as completed."""
        self.status = PaymentStatus.COMPLETED
        if transaction_id:
            self.transaction_id = transaction_id
        if payment_intent_id:
            self.payment_intent_id = payment_intent_id
        if charge_id:
            self.charge_id = charge_id
        self.save(update_fields=[
            "status",
            "transaction_id",
            "payment_intent_id",
            "charge_id",
            "updated_at"
        ])
        
        # Update order status
        self.order.mark_as_paid()
    
    def mark_as_failed(self, error_code="", error_message=""):
        """Mark payment as failed."""
        self.status = PaymentStatus.FAILED
        self.error_code = error_code
        self.error_message = error_message
        self.save(update_fields=["status", "error_code", "error_message", "updated_at"])
    
    def process_refund(self, amount=None, reason=""):
        """
        Process a refund for this payment.
        
        Args:
            amount: Amount to refund (None for full refund)
            reason: Reason for refund
        
        Returns:
            bool: True if refund was successful
        """
        if amount is None:
            amount = self.refundable_amount
        
        if amount > self.refundable_amount:
            raise ValueError("Refund amount exceeds refundable amount")
        
        # Future: Implement Stripe refund via Celery task
        # from .tasks import process_stripe_refund
        # process_stripe_refund.delay(self.id, amount, reason)
        
        self.refunded_amount += amount
        self.refund_reason = reason
        
        if self.refunded_amount >= self.amount:
            self.status = PaymentStatus.REFUNDED
        else:
            self.status = PaymentStatus.PARTIALLY_REFUNDED
        
        self.save(update_fields=[
            "refunded_amount",
            "refund_reason",
            "status",
            "updated_at"
        ])
        
        return True


class PaymentLog(TimeStampedModel):
    """
    Payment log model for audit trail.
    Records all payment-related events for debugging and compliance.
    """
    
    class LogLevel(models.TextChoices):
        INFO = "info", _("Info")
        WARNING = "warning", _("Warning")
        ERROR = "error", _("Error")
        DEBUG = "debug", _("Debug")
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name=_("payment")
    )
    level = models.CharField(
        max_length=20,
        choices=LogLevel.choices,
        default=LogLevel.INFO,
        verbose_name=_("level")
    )
    event = models.CharField(
        max_length=100,
        verbose_name=_("event")
    )
    message = models.TextField(
        verbose_name=_("message")
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("data")
    )
    
    class Meta:
        verbose_name = _("payment log")
        verbose_name_plural = _("payment logs")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.payment.id} - {self.event} - {self.level}"


class Refund(TimeStampedModel):
    """
    Refund model for tracking individual refund transactions.
    Supports partial and multiple refunds per payment.
    """
    
    class RefundStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="refunds",
        verbose_name=_("payment")
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("amount")
    )
    reason = models.TextField(
        verbose_name=_("reason")
    )
    status = models.CharField(
        max_length=20,
        choices=RefundStatus.choices,
        default=RefundStatus.PENDING,
        verbose_name=_("status")
    )
    
    # External IDs
    refund_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("refund transaction ID")
    )
    
    # Processed by
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_refunds",
        verbose_name=_("processed by")
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("processed at")
    )
    
    class Meta:
        verbose_name = _("refund")
        verbose_name_plural = _("refunds")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Refund {self.id} - {self.payment.order.order_number} - ${self.amount}"
