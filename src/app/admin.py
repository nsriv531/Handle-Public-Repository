"""
app.admin Module

This module contains Django admin configurations for managing Lead records.
It registers the Lead model with the admin site, allowing administrators to
view and manage Lead records through the Django admin interface.
"""

from django.contrib import admin

from .models import Lead

admin.site.register(Lead)
