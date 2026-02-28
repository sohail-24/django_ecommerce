"""
Payments Views
Payment processing and Stripe integration views.
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.orders.models import Order

from .models import Payment, PaymentLog, PaymentStatus

logger = logging.getLogger(__name__)


class PaymentProcessView(LoginRequiredMixin, View):
    """
    Payment processing view.
    
    Creates a payment record and initializes Stripe checkout session.
    """
    
    template_name = "payments/process.html"
    
    def get(self, request, order_number, *args, **kwargs):
        order = get_object_or_404(
            Order,
            order_number=order_number,
            user=request.user
        )
        
        # Check if order is already paid
        if order.is_paid:
            messages.info(request, _("This order has already been paid."))
            return redirect("orders:order_detail", order_number=order.order_number)
        
        # Get or create payment
        payment, created = Payment.objects.get_or_create(
            order=order,
            status__in=[PaymentStatus.PENDING, PaymentStatus.PROCESSING],
            defaults={
                "user": request.user,
                "amount": order.total,
                "currency": order.currency,
                "payment_method": "stripe",
                "billing_email": order.email,
                "billing_name": order.shipping_full_name,
                "description": f"Order {order.order_number}",
                "ip_address": self.get_client_ip(request),
            }
        )
        
        # Create Stripe PaymentIntent (if Stripe is configured)
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        client_secret = None
        
        if settings.STRIPE_SECRET_KEY:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total * 100),  # Convert to cents
                    currency=order.currency.lower(),
                    metadata={
                        "order_number": order.order_number,
                        "payment_id": payment.id,
                    },
                    description=f"Order {order.order_number}",
                    receipt_email=order.email,
                )
                
                payment.payment_intent_id = intent.id
                payment.save(update_fields=["payment_intent_id"])
                client_secret = intent.client_secret
                
            except Exception as e:
                logger.error(f"Stripe PaymentIntent creation failed: {e}")
                PaymentLog.objects.create(
                    payment=payment,
                    level=PaymentLog.LogLevel.ERROR,
                    event="payment_intent_creation_failed",
                    message=str(e),
                )
        
        return render(request, self.template_name, {
            "order": order,
            "payment": payment,
            "stripe_public_key": stripe_public_key,
            "client_secret": client_secret,
        })
    
    def post(self, request, order_number, *args, **kwargs):
        """Handle payment confirmation."""
        order = get_object_or_404(
            Order,
            order_number=order_number,
            user=request.user
        )
        
        payment_intent_id = request.POST.get("payment_intent_id")
        
        if payment_intent_id and settings.STRIPE_SECRET_KEY:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                
                if intent.status == "succeeded":
                    payment = Payment.objects.get(payment_intent_id=payment_intent_id)
                    payment.mark_as_completed(
                        transaction_id=intent.charges.data[0].id if intent.charges.data else "",
                        charge_id=intent.charges.data[0].id if intent.charges.data else "",
                    )
                    
                    # Log success
                    PaymentLog.objects.create(
                        payment=payment,
                        level=PaymentLog.LogLevel.INFO,
                        event="payment_succeeded",
                        message=f"Payment succeeded for order {order.order_number}",
                        data={"payment_intent_id": payment_intent_id},
                    )
                    
                    messages.success(request, _("Payment successful!"))
                    return redirect("payments:success", order_number=order.order_number)
                
                else:
                    messages.error(request, _("Payment was not successful. Please try again."))
                    return redirect("payments:process", order_number=order.order_number)
                    
            except Exception as e:
                logger.error(f"Payment confirmation failed: {e}")
                messages.error(request, _("Payment processing failed. Please try again."))
                return redirect("payments:process", order_number=order.order_number)
        
        # Simulate payment success for development (when Stripe is not configured)
        if not settings.STRIPE_SECRET_KEY:
            payment = Payment.objects.filter(order=order).first()
            if payment:
                payment.mark_as_completed(transaction_id="SIMULATED")
                messages.success(request, _("Payment successful! (Simulated)"))
                return redirect("payments:success", order_number=order.order_number)
        
        messages.error(request, _("Payment processing failed."))
        return redirect("payments:process", order_number=order.order_number)
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    """Display payment success page."""
    
    template_name = "payments/success.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = kwargs.get("order_number")
        context["order"] = get_object_or_404(
            Order,
            order_number=order_number,
            user=self.request.user
        )
        return context


class PaymentCancelView(LoginRequiredMixin, View):
    """Handle payment cancellation."""
    
    def get(self, request, order_number, *args, **kwargs):
        order = get_object_or_404(
            Order,
            order_number=order_number,
            user=request.user
        )
        
        # Update payment status
        Payment.objects.filter(
            order=order,
            status=PaymentStatus.PENDING
        ).update(status=PaymentStatus.CANCELLED)
        
        messages.warning(request, _("Payment was cancelled."))
        return redirect("orders:checkout")


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook handler.
    
    Handles Stripe webhook events for payment status updates.
    """
    
    def post(self, request, *args, **kwargs):
        """Handle Stripe webhook events."""
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        
        if not settings.STRIPE_WEBHOOK_SECRET:
            logger.warning("Stripe webhook secret not configured")
            return HttpResponse(status=400)
        
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return HttpResponse(status=400)
        
        # Handle the event
        if event["type"] == "payment_intent.succeeded":
            self.handle_payment_intent_succeeded(event["data"]["object"])
        
        elif event["type"] == "payment_intent.payment_failed":
            self.handle_payment_intent_failed(event["data"]["object"])
        
        elif event["type"] == "charge.refunded":
            self.handle_charge_refunded(event["data"]["object"])
        
        return HttpResponse(status=200)
    
    def handle_payment_intent_succeeded(self, payment_intent):
        """Handle successful payment intent."""
        payment_intent_id = payment_intent["id"]
        
        try:
            payment = Payment.objects.get(payment_intent_id=payment_intent_id)
            
            # Get charge ID
            charge_id = ""
            if payment_intent.get("charges", {}).get("data"):
                charge_id = payment_intent["charges"]["data"][0]["id"]
            
            payment.mark_as_completed(
                transaction_id=charge_id,
                charge_id=charge_id,
            )
            
            # Update card info if available
            if payment_intent.get("charges", {}).get("data"):
                charge = payment_intent["charges"]["data"][0]
                if charge.get("payment_method_details", {}).get("card"):
                    card = charge["payment_method_details"]["card"]
                    payment.card_last_four = card.get("last4", "")
                    payment.card_brand = card.get("brand", "")
                    payment.save(update_fields=["card_last_four", "card_brand"])
            
            PaymentLog.objects.create(
                payment=payment,
                level=PaymentLog.LogLevel.INFO,
                event="webhook_payment_succeeded",
                message=f"Payment succeeded via webhook",
                data={"payment_intent_id": payment_intent_id},
            )
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for intent: {payment_intent_id}")
    
    def handle_payment_intent_failed(self, payment_intent):
        """Handle failed payment intent."""
        payment_intent_id = payment_intent["id"]
        
        try:
            payment = Payment.objects.get(payment_intent_id=payment_intent_id)
            
            error = payment_intent.get("last_payment_error", {})
            payment.mark_as_failed(
                error_code=error.get("code", ""),
                error_message=error.get("message", ""),
            )
            
            PaymentLog.objects.create(
                payment=payment,
                level=PaymentLog.LogLevel.ERROR,
                event="webhook_payment_failed",
                message=error.get("message", "Payment failed"),
                data={"payment_intent_id": payment_intent_id},
            )
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for intent: {payment_intent_id}")
    
    def handle_charge_refunded(self, charge):
        """Handle refunded charge."""
        charge_id = charge["id"]
        
        try:
            payment = Payment.objects.get(charge_id=charge_id)
            
            # Update refund amount
            refunded_amount = charge.get("amount_refunded", 0) / 100  # Convert from cents
            payment.refunded_amount = refunded_amount
            
            if refunded_amount >= payment.amount:
                payment.status = PaymentStatus.REFUNDED
            else:
                payment.status = PaymentStatus.PARTIALLY_REFUNDED
            
            payment.save(update_fields=["refunded_amount", "status"])
            
            PaymentLog.objects.create(
                payment=payment,
                level=PaymentLog.LogLevel.INFO,
                event="webhook_charge_refunded",
                message=f"Charge refunded: ${refunded_amount:.2f}",
                data={"charge_id": charge_id, "refunded_amount": refunded_amount},
            )
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for charge: {charge_id}")
