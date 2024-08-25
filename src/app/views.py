"""
Authentication and Authorization Views.
Entry point to web applications.
Designed to handle signup and login routing
as well as account managment.
"""

from allauth.account.views import SignupView, LoginView, ConfirmEmailView, EmailView
from allauth.account.models import EmailAddress
from django.views import View
from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseForbidden
from studio_suite.models import StudioInfo, MemberStudioRelationship
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RestrictedUserChangeForm
from django.views.generic.edit import UpdateView

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

class IndexView(View):
    """
    Description:
        First page served at base url.
    """

    template_name = 'app/index.html'

    def get(self, request):
        """
        Description:
            Returns the index html template.
            Studios that the user is related to.
        
        Security:
            TODO: If studio relationship stay we should removed the studio's UUID from
            the context object.
        """

        # During Development, retrieve studio information to display login/signup links.
        studios = StudioInfo.objects.all()

        return render(request, self.template_name, context = {'studios': studios})



class ExtendedLoginView(LoginView):
    """
    Description:
        Extended functionality for allauth login view.
        Attaches each studio's unique URL extension to the end of the route.
        Directs members to the MemberSuite and studios to the StudioSuite.
        Associates global members to the studio on first login.
    """

    template_name = 'account/login-portal.html'


    def dispatch(self, request, *args, **kwargs):
        """
        Description:
            Check if the user is already logged in and redirect them appropriately if so.
        
        Returns:
            A redirect to the desired internal access path based on membership or ownership.
        """
        if request.user.is_authenticated:
            studio_url_extension = self.kwargs.get('studio_url_extension')

            try:
                if StudioInfo.objects.get(url_extension=studio_url_extension, linked_account=request.user):
                    return redirect('studio_home', studio_url_extension=studio_url_extension)
            except StudioInfo.DoesNotExist:
                if MemberStudioRelationship.objects.filter(member=request.user, studio__url_extension=studio_url_extension).exists():
                    return redirect('member_home', studio_url_extension=studio_url_extension)
                else:
                    studio = get_object_or_404(StudioInfo, url_extension=studio_url_extension)
                    MemberStudioRelationship.objects.create(member=request.user, studio=studio, member_role=studio.new_member_role)
                    return redirect('member_home', studio_url_extension=studio_url_extension)

        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        """
        Description:
            Retrieves and prepares additional context data to be passed to the template.
        
        Returns:
            Studio Info
        
        Security:
            TODO: Remove Studio UUID from context object
        """
        context = super().get_context_data(**kwargs)
        studio_url_extension = self.kwargs.get('studio_url_extension')

        if studio_url_extension:
            studio = get_object_or_404(StudioInfo, url_extension=studio_url_extension)
            context['studio'] = studio

        return context


    def form_valid(self, form):
        """
        Description:
            Determines the user's role and associations with a studio based on the provided 'studio_url_extension'.
        
        Returns:
            TODO
        """
        super().form_valid(form)
        req_user = self.request.user
        studio_url_extension = self.kwargs.get('studio_url_extension')

        if not studio_url_extension or not req_user.is_authenticated:
            return redirect('account_logout')

        try:
            studio = StudioInfo.objects.get(url_extension=studio_url_extension, linked_account=req_user)
            return redirect('studio_home', studio_url_extension=studio_url_extension)
        except StudioInfo.DoesNotExist:
            if MemberStudioRelationship.objects.filter(member=req_user, studio__url_extension=studio_url_extension).exists():
                return redirect('member_home', studio_url_extension=studio_url_extension)
            else:
                studio = get_object_or_404(StudioInfo, url_extension=studio_url_extension)
                MemberStudioRelationship.objects.create(member=req_user, studio=studio, member_role=studio.new_member_role)
                return redirect('member_home', studio_url_extension=studio_url_extension)



class MemberSignupView(SignupView):
    """
    Description:    
        Signup View for managing new members and extending allauth functionality.
    """

    template_name = 'account/member-signup.html'

    def get_context_data(self, **kwargs):
        """
        Description:
            Retrieves and prepares additional context data to be passed to the template.
        
        Security:
            TODO: Remove studio UUID from context object.
        """

        # Get initial context.
        context = super().get_context_data(**kwargs)
        studio_url_extension = self.kwargs.get('studio_url_extension')

        # If studio_url_extension is provided and valid.
        if studio_url_extension:
            studio = get_object_or_404(StudioInfo, url_extension=studio_url_extension)
            context['studio'] = studio

        return context


    def form_valid(self, form):
        """
        Description:
            Processes a valid MEMBER registration form submission.
            It ensures that the user is assigned the 'MEMBER' role, associates them with
            the specific studio based on the 'studio_url_extension',
            and performs an automatic login to that studio.
        """

        # Call parent form_valid method to verify the form.
        response = super().form_valid(form)

        user = self.user

        # Verify the provided studio_url_extension
        studio_url_extension = self.kwargs['studio_url_extension']
        studio = get_object_or_404(StudioInfo, url_extension=studio_url_extension)

        MemberStudioRelationship.objects.get_or_create(member=user, studio=studio, member_role=studio.new_member_role)

        # Once operations are completed successfully, login the member
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        return response



class StudioSignupView(SignupView):
    """
    Description:
        Signup view for creating new studios and extending allauth functionality.
    """

    template_name = 'account/studio-signup.html'

    def form_valid(self, form):
        """
        Description:
            Validation of studio account creation form. It ensures that the user is
            assigned the 'STUDIO' role and logs them in automatically.
        """

        # Call the parent class's form_valid method to verify the form.
        response = super().form_valid(form)

        # Log in the user automatically.
        login(self.request, self.user, backend='django.contrib.auth.backends.ModelBackend')

        return response

    def get_email_confirmation_url(self):
        """
        Description:
            This method returns the URL for the email verification sent page after
            successful studio registration.
        """

        return reverse_lazy('account_email_verification_sent')



class ExtendedConfirmEmailView(ConfirmEmailView):
    """
    Description:
        Customized Confirm Email Page - Bypass allauth built-in redirect.
    """

    def post(self, *args, **kwargs):
        """ 
        Description:
            Verify email and redirect based on group upon Confirmation.
        """
        self.object = self.get_object()
        self.object.confirm(self.request)
        req_user = self.object.email_address.user

        # Mark the confirmed email address as verified
        self.object.email_address.verified = True
        self.object.email_address.save()

        # Fetch all StudioRelationships for the user
        user_relationships = MemberStudioRelationship.objects.filter(member=req_user)
        num_emails = EmailAddress.objects.filter(user=req_user).count()

        if user_relationships.count() == 1 and num_emails == 1:
            # If there is exactly one relationship, retrieve the custom_url_extension field
            # num_emails = 1 means this a signup request
            first_relationship = user_relationships.first()
            studio = first_relationship.studio
            studio_url_extension = studio.url_extension
            # Redirect to a URL based on the custom_url_extension value
            return redirect('member_home', studio_url_extension=studio_url_extension)
        elif user_relationships.count() == 0 and num_emails == 1:
            # If there's no relationship, redirect to the studio info page
            # num_emails = 1 means this a signup request
            return redirect('studio_info')
        else:
            # num_emails != 1 means this a custom new email request 
            # (since they can't reverify or delete a single verified email)
            # this also means relationships dont matter because they got
            # to this request through their profile.
            return redirect('account_email')



class ExtendedUserProfileView(LoginRequiredMixin, UpdateView):
    """
    Description:
        User profile view, allows them to see
        their studios and route to links for account
        management.
    """
    template_name = 'account/user-profile.html'
    form_class = RestrictedUserChangeForm
    success_url = reverse_lazy('user_profile')

    def get_object(self, queryset=None):
        """
        Description:
            Retrieve the user object associated with the current request.
        """
        return self.request.user


    def form_valid(self, form):
        """
        Description:
            Process a valid form submission.
        """
        # Add any additional logic here if needed
        return super().form_valid(form)


    def get(self, *args, **kwargs):
        """
        Description:
            Render the necessary information for the signed-in user.
        """

        # Temp: Show all studios the user is associated with.
        member_studios = MemberStudioRelationship.objects.filter(member=self.request.user)
        owner_studios = StudioInfo.objects.filter(linked_account=self.request.user)
        
        # Create the context dictionary
        self.context = {
            'form': self.form_class(instance=self.request.user),  # Pass the form instance to the template
            'member_studios': member_studios,
            'owner_studios': owner_studios,
        }

        return render(self.request, self.template_name, self.context)



class ExtendedPasswordResetView(PasswordResetView):
    """
    Description:
        Custom templates for the password reset
        and the email sent along with it.
    """
    template_name = 'account/account_recovery/password-reset.html'
    email_template_name = 'account/account_recovery/password-reset-email.html'
    subject_template_name = 'account/account_recovery/password-reset-subject.txt'



class ExtendedPasswordResetDoneView(PasswordResetDoneView):
    """
    Description:
        Custom template for password reset done.
    """
    template_name = 'account/account_recovery/password-reset-sent.html'



class ExtendedPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Description:
        Custom template for confirming the password reset.
    """
    template_name = 'account/account_recovery/password-reset-confirm.html'



class ExtendedPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Description:
        Custom template for the password reset complete view.
    """
    template_name = 'account/account_recovery/password-reset-complete.html'


class ProfileLoginView(LoginView):
    """
    Description:
        Allows users to log directly into their profile.
        This way is they lose login links they can just
        log into their profile and reroute themselves
        to the correct studio.
    """
    template_name = 'account/profile-login.html'

    def get_success_url(self):
        """
        Description:
            Changes the login success route to the
            users profile instead of the allauth
            email route.
        """
        return reverse_lazy('user_profile')


class ExtendedEmailView(EmailView):
    """
    Description:
        Allows users to log directly into their profile.
        This way is they lose login links they can just
        log into their profile and reroute themselves
        to the correct studio.
    """
    template_name = "account/account_recovery/email-reset.html"



def temp_signup_fix():
    """ Read message below: 
    + We've overriden the template so I'm not really sure
    why it's required still but I don't think it's a harm.
    """

    message = """
    This page is an artifact of allauth, this happens because some allauth<br>
    views require a reverse to an 'account_signup' view<br>
    however we have built two custom signups with custom view names<br>
    """
    return HttpResponseForbidden(f'<h1>Blocked</h1> {message}')
