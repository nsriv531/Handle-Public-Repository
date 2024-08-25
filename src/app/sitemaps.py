"""
Engine crawling static views for efficiency.
"""

from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse



class StaticViewSitemap(Sitemap):
    """
    Description:
        Sitemap class for generating URLs of static views.
    """
    def items(self):
        """
        Description:
            Returns a list of items (view names) to include in the sitemap.
        """
        return []

    def location(self, item):
        """
        Description:
            Generates the URL for a given view based on its name.
        """
        return reverse(item)
