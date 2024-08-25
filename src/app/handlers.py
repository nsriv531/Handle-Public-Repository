"""
Unused - Left as comments for reference.

Commonly used for:
Custom Exception Handling
Middleware Processing
Signal Handlers
Event Handling
Batch Processing
"""

# from django.contrib.auth.models import User
# from django.core.mail import mail_managers
# from django.dispatch import receiver
# from django.utils import timezone

# from store.signals import user_purchase
# from teachers.signals import user_signup # DNE


# @receiver(user_signup)
# def notify_user_signup(sender, **kwargs):
#     user_id = kwargs.get('user_id')

#     user: User = User.objects.get(id=user_id)
#     subject = f'New user signup: {user.email}'
#     message = f"""
#     New user signup: {user.email}
#     Time: {timezone.now()}
#     """
#     mail_managers(subject=subject,
#                   message=message,
#                   fail_silently=False,
#                   connection=None,
#                   html_message=None)


# @receiver(user_purchase)
# def notify_user_purchase(sender, **kwargs):
#     product_id = kwargs.get('product_id')
#     payment_id = kwargs.get('payment_id')

#     subject = f'New purchase: {product_id}'
#     message = f"""
#     Product: {product_id}
#     Payment: {payment_id}
#     Time: {timezone.now()}
#     """
#     mail_managers(subject=subject,
#                   message=message,
#                   fail_silently=False,
#                   connection=None,
#                   html_message=None)
