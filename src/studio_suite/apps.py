"""
This module defines the configuration for the 'studio_suite' Django application.
It specifies the app's name and database field configuration.
"""

from django.apps import AppConfig



class StudiosuiteConfig(AppConfig):
    """
    Description:
        This class represents the configuration for the 'StudioSuite' app in your Django project.
        It defines the app's name and specifies the default AutoField for its models.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studio_suite'
