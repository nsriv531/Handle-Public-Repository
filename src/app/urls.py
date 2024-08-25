"""
Primary URL routing, mapping and indexing.
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.urls import re_path
from django.views.generic.base import TemplateView
from django.views.static import serve
from django.views.generic.base import RedirectView
from allauth.account.views import (
    LoginView,
    LogoutView,
    EmailVerificationSentView,
    ConfirmEmailView
)

# from django.contrib.auth.views import (
#     PasswordResetView,
#     PasswordResetDoneView,
#     PasswordResetConfirmView,
#     PasswordResetCompleteView,
# )

from .views import (
    MemberSignupView,
    StudioSignupView,
    ExtendedLoginView,
    ExtendedConfirmEmailView,
    ExtendedUserProfileView,
    IndexView,
    temp_signup_fix,
    ExtendedPasswordResetView,
    ExtendedPasswordResetDoneView,
    ExtendedPasswordResetConfirmView,
    ExtendedPasswordResetCompleteView,
    ProfileLoginView,
    ExtendedEmailView,
)
from app.sitemaps import StaticViewSitemap

urlpatterns = [
    # Original Provided Routes
    path('store/', include('store.urls')),
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True)),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', sitemap, {'sitemaps': {'static': StaticViewSitemap}}),

    # Primary Page - Studios will be directed here to learn about handle:
    path('', IndexView.as_view(), name='index'),

    # Routes for seperating internal applications:
    path('member-suite/', include('member_suite.urls'), name='member_suite'),
    path('studio-suite/', include('studio_suite.urls'), name='studio_suite'),

    # Custom Allauth routes:
    path('accounts/login-portal/<str:studio_url_extension>/', ExtendedLoginView.as_view(), name='login_portal'),
    path('accounts/member-signup/<str:studio_url_extension>/', MemberSignupView.as_view(), name='member_signup'),
    path('accounts/studio-signup/', StudioSignupView.as_view(), name='studio_signup'),
    path('accounts/confirm-email/<str:key>/', ExtendedConfirmEmailView.as_view(), name='account_confirm_email'),
    path('accounts/profile-login/', ProfileLoginView.as_view(), name='account_login'),
    path('accounts/user-profile', ExtendedUserProfileView.as_view(), name='user_profile'),
    path('accounts/password/reset/', ExtendedPasswordResetView.as_view(), name='account_reset_password'),
    path('accounts/password/reset/done/', ExtendedPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/password/reset/confirm/<uidb64>/<token>/', ExtendedPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/password/reset/complete/', ExtendedPasswordResetCompleteView.as_view(), name='password_reset_complete'),
 
    # Required allauth base routes:
    path('accounts/logout/', LogoutView.as_view(), name='account_logout'),
    path('accounts/email/', ExtendedEmailView.as_view(), name='account_email'),
    path('account/email/verification/sent/', EmailVerificationSentView.as_view(), name='account_email_verification_sent'),

    # Allauth reverse requirement to account_signup - shouldnt be needed anymore but for some reason it is.
    path('accounts/temp-signup-fix/', temp_signup_fix, name='account_signup'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('^__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns += [
    re_path(
        r'^static/(?P<path>.*)$',
        serve,
        {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': True
        },
    )
]
