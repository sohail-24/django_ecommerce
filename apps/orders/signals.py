"""
Orders Signals
Signal handlers for order-related events.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order


@receiver(post_save, sender=Order)
def send_order_confirmation(sender, instance, created, **kwargs):
    """Send order confirmation email when order is created."""
    if created:
        # Future: Send order confirmation email via Celery
        # from .tasks import send_order_confirmation_email
        # send_order_confirmation_email.delay(instance.id)
        pass


@receiver(post_save, sender=Order)
def notify_staff_on_new_order(sender, instance, created, **kwargs):
    """Notify staff when a new order is placed."""
    if created:
        # Future: Send notification to staff via Celery
        # from .tasks import notify_staff_new_order
        # notify_staff_new_order.delay(instance.id)
        pass
