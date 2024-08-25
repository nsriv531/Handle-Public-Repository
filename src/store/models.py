"""
Unused - Left as provided for reference.
"""

from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL



class Product(models.Model):
    """
    Unused - Left as provided for reference.
    """

    name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    description = models.CharField(max_length=200)
    url = models.URLField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    class Meta:
        ordering = ('-created_at',)



    def __str__(self):
        """
        Unused - Left as provided for reference.
        """

        return self.name



class Price(models.Model):
    """
    Unused - Left as provided for reference.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        """
        Unused - Left as provided for reference.
        """

        return f"{self.product.name} {self.price}"



class Payment(models.Model):
    """
    Unused - Left as provided for reference.
    """

    PENDING = 'P'
    COMPLETED = 'C'
    FAILED = 'F'

    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (COMPLETED, 'completed'),
        (FAILED, 'failed'),
    )

    user_email = models.EmailField(unique=True)
    user_id = models.IntegerField()

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    payment_status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        """
        Unused - Left as provided for reference.
        """

        return self.product.name
