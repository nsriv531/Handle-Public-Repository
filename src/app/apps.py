"""
This module defines the configuration for the 'app' Django application.
It specifies the app's name, database field configuration, and includes a 'ready'
method for any additional setup to be performed when the app is loaded.
"""

from django.apps import AppConfig



class AppConfig(AppConfig):
    """
    Defines the app's name and specifies a custom 'ready' method for any necessary
    setup when the app is loaded.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    # def ready(self):
    #     """
    #     Called when the 'app' is ready to perform any additional
    #     setup, such as importing custom handlers or connecting signals.
    #     """
    #     import app.handlers  # noqa
