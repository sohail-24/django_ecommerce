"""
Payments Admin Configuration
Admin interface for Payment and related models.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Payment, PaymentLog, Refund


class PaymentLogInline(admin.TabularInline):
    """Inline admin for payment logs."""
    model = PaymentLog
    extra = 0
    readonly_fields = ["level", "event", "message", "created_at"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class RefundInline(admin.TabularInline):
    """Inline admin for refunds."""
    model = Refund
    extra = 0
    readonly_fields = ["processed_at"]
    fields = [
        "amount",
        "reason",
        "status",
        "refund_transaction_id",
        "processed_by",
        "processed_at",
    ]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment admin configuration."""

    list_display = [
        "id",
        "order",
        "amount_display",
        "payment_method",
        "status",
        "transaction_id_short",
        "created_at",
    ]

    list_filter = [
        "status",
        "payment_method",
        "currency",
        "created_at",
    ]

    search_fields = [
        "order__order_number",
        "transaction_id",
        "payment_intent_id",
        "charge_id",
        "user__email",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "refundable_amount",
    ]

    date_hierarchy = "created_at"
    inlines = [RefundInline, PaymentLogInline]

    fieldsets = (
        (None, {
            "fields": (
                "order",
                "user",
                "amount",
                "currency",
                "payment_method",
                "status",
            )
        }),
        (_("Transaction IDs"), {
            "fields": (
                "transaction_id",
                "payment_intent_id",
                "charge_id",
            )
        }),
        (_("Card Information"), {
            "fields": (
                "card_last_four",
                "card_brand",
            )
        }),
        (_("Billing Information"), {
            "fields": (
                "billing_email",
                "billing_name",
            )
        }),
        (_("Refund Information"), {
            "fields": (
                "refunded_amount",
                "refund_reason",
            )
        }),
        (_("Error Information"), {
            "fields": (
                "error_code",
                "error_message",
            ),
            "classes": ("collapse",),
        }),
        (_("Metadata"), {
            "fields": (
                "description",
                "metadata",
                "ip_address",
            ),
            "classes": ("collapse",),
        }),
    )

    actions = [
        "mark_as_completed",
        "mark_as_failed",
    ]

    def amount_display(self, obj):
        return f"${obj.amount:.2f}"
    amount_display.short_description = _("Amount")

    def transaction_id_short(self, obj):
        if obj.transaction_id:
            return obj.transaction_id[:20] + "..."
        return "-"
    transaction_id_short.short_description = _("Transaction ID")

    @admin.action(description=_("Mark selected payments as completed"))
    def mark_as_completed(self, request, queryset):
        for payment in queryset:
            payment.mark_as_completed()

    @admin.action(description=_("Mark selected payments as failed"))
    def mark_as_failed(self, request, queryset):
        queryset.update(status="failed")


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Refund admin configuration."""

    list_display = [
        "id",
        "payment",
        "amount",
        "status",
        "processed_by",
        "processed_at",
        "created_at",
    ]

    list_filter = ["status", "created_at"]
    search_fields = ["payment__order__order_number", "reason"]
    raw_id_fields = ["payment", "processed_by"]
    readonly_fields = ["processed_at"]


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    """Payment log admin configuration."""

    list_display = [
        "payment",
        "level",
        "event",
        "message_short",
        "created_at",
    ]

    list_filter = ["level", "event", "created_at"]
    search_fields = ["payment__id", "event", "message"]
    raw_id_fields = ["payment"]
    readonly_fields = [
        "payment",
        "level",
        "event",
        "message",
        "data",
        "created_at",
    ]

    def message_short(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_short.short_description = _("Message")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False