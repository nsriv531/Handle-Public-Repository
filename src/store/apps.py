"""
Unused - Left as provided for reference.
"""

from django.apps import AppConfig



class AppConfig(AppConfig):
    """
    Unused - Left as provided for reference.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        """
        Unused - Left as provided for reference.
        """

        import store.signals  # noqa
