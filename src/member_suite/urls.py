"""
member_suite URL routing, mapping and indexing.
"""

from django.urls import path

from .views import (
    MemberHomeView,
    BookAKilnView,
)

urlpatterns = [
    path('home/<str:studio_url_extension>', MemberHomeView.as_view(), name='member_home'),
    path('book-a-kiln/<str:studio_url_extension>', BookAKilnView.as_view(), name='book_a_kiln'),
]
