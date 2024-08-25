"""
Unused - Left as provided for reference.
"""

from django.urls import path
from store.views import PurchaseView, SuccessView, CancelView, StripeWebhookView

urlpatterns = [
    path('', PurchaseView.as_view(), name='purchase'),
    path('success/', SuccessView.as_view(), name='purchase_success'),
    path('cancel/', CancelView.as_view(), name='purchase_cancel'),
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe_webhook'),
]
