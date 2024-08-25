"""
Unused - Left as provided for reference.
"""

import logging
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .models import Price, Product, Payment
from .signals import user_purchase

stripe.api_key = settings.STRIPE_SECRET

logger = logging.getLogger(settings.LOGGER_NAME)



class PurchaseView(View):
    """
    Unused - Left as provided for reference.
    """

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """
        Unused - Left as provided for reference.
        """

        products = {}

        for product in Product.objects.all():
            products[product] = Price.objects.filter(product=product)

        return render(request, 'store/purchase.html', {
            'products': products
        })

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """
        Create a checkout session and redirect the user to Stripe's checkout page
        """

        price = Price.objects.get(id=request.POST.get('pk'))

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(price.price) * 100,
                        'product_data': {
                            'name': price.product.name,
                            'description': price.product.description
                        },
                    },
                    'quantity': 1,
                }
            ],
            metadata={
                'product_id': price.product.id,
                'user_id': request.user.id
            },
            mode='payment',
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )
        return redirect(checkout_session.url)



class SuccessView(TemplateView):
    """
    Unused - Left as provided for reference.
    """

    template_name = 'store/success.html'



class CancelView(TemplateView):
    """
    Unused - Left as provided for reference.
    """

    template_name = 'store/cancel.html'



@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """
    Stripe webhook view to handle checkout session completed event.
    """

    def post(self, request, *args, **kwargs):
        """
        Unused - Left as provided for reference.
        """

        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            logger.info('Payment successful')

            session = event['data']['object']
            customer_email = session['customer_details']['email']
            product_id = session['metadata']['product_id']
            user_id = session['metadata']['user_id']
            product: Product = get_object_or_404(Product, id=product_id)

            # TODO: using user_id, find the corresponding user and grant the product to their account.
            # Next, record payment, and send signal to notify other apps of the purchase.
            # To avoid failure modes, use a transaction to wrap the entire operation.

            payment = Payment.objects.create(
                user_email=customer_email,
                user_id=user_id,
                product=product,
                payment_status='completed'
            )

            user_purchase.send(sender=self.__class__, product_id=product_id, payment_id=payment.id)

        return HttpResponse(status=200)
