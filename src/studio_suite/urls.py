"""
studio_suite URL routing, mapping and indexing.
"""

from django.urls import path

from .views import (
    StudioHomeView,
    GetStudioInfoView,
    KilnManagementView,
    MemberManagementView,
    TimeslotManagementView,
    UpdateStudioInfoView
)

urlpatterns = [
    path('get-studio-info/', GetStudioInfoView.as_view(), name="studio_info"),
    path('update-studio-info/<str:studio_url_extension>', UpdateStudioInfoView.as_view(), name='update_studio_info'),
    path('home/<str:studio_url_extension>', StudioHomeView.as_view(), name='studio_home'),
    path('kiln-management/<str:studio_url_extension>', KilnManagementView.as_view(), name='kiln_management'),
    path('member-management/<str:studio_url_extension>', MemberManagementView.as_view(), name='member_management'),
    path('timeslot-management/<str:studio_url_extension>', TimeslotManagementView.as_view(), name='timeslot_management')
]
