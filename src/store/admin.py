"""
Unused - Left as provided for reference.
"""

from django.contrib import admin
from .models import Price, Product



class PriceAdmin(admin.StackedInline):
    """
    Unused - Left as provided for reference.
    """

    model = Price



class ProductAdmin(admin.ModelAdmin):
    """
    Unused - Left as provided for reference.
    """

    inlines = (PriceAdmin,)

    class Meta:
        """
        Unused - Left as provided for reference.
        """

        model = Product

admin.site.register(Product)
admin.site.register(Price)
