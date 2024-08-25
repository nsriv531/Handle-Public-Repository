"""
This module will contain Django admin configurations for managing member_suite specific
models and their data through the Django admin interface. 
"""

from django.contrib import admin
from .models import BookingManagement

class BookingManagementAdmin(admin.ModelAdmin):
    """
    Description:
        Manage how the admin page displays and allows interaction with bookings.
    """
    list_display = ('studio', 'member', 'timeslot', 'booking_date')
    list_filter = ('studio', 'member', 'booking_date')
    search_fields = ('studio__name', 'member__username', 'timeslot__name', 'booking_date')

admin.site.register(BookingManagement, BookingManagementAdmin)
