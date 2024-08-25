"""
This module defines the configuration for the 'member_suite' Django application.
It specifies the app's name and database field configuration.
"""

from django.apps import AppConfig



class MembersuiteConfig(AppConfig):
    """
    Description:
        Configuration class for the 'member_suite' Django app.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'member_suite'
