"""
Studio Suite Views for Studio Management

The Studio Suite Views provide comprehensive functionalities for studio management.
Studio owners and administrators can utilize these views to configure and control
various aspects of their studio, such as member management, timeslot scheduling,
and other administrative tasks. These views serve as the core tools within the studio_suite,
offering a centralized platform for effective studio management.
-testcommit
"""

from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from app.decorators import studio_ownership_required
from django.urls import reverse
from django.contrib import messages
from .models import (
    StudioInfo,
    MemberStudioRelationship,
    KilnRange,
    KilnManagement,
    TimeslotManagement,
    #TimeslotBlackout
)
from .forms import (
    StudioInfoForm,
    KilnManagementForm,
    KilnRangeForm,
    TimeslotManagementForm,
    #TimeslotBlackoutForm,
    MemberRoleChangeForm,
    DeleteMemberForm,
    KilnRangeDeleteForm,
    KilnDeleteForm,
    DeleteTimeslotForm,
)
from datetime import (
    datetime,
    timedelta,
    date,
)

@method_decorator(login_required, name="dispatch")
class GetStudioInfoView(View):
    """
    Description
        View class to handle the creation of a studio record to collect basic data.
        This data is required to take studios public.

    Security:
        Must be logged into a valid account to create a studio.
        TODO
        - Confirm this cannot be submitted twice in some weird attempt to create duplicate
          studios.
        - Make sure once after this has been created for the first time that only
          bio, studio name, and new_member_roles can be modified.


    TODO
    - Needs to be routed here after after an account recovery for studios but only
      when this hasnt been filled out.
    - Needs to be accessible from the studio suite so studio's can modify their
      bio, studio name, and new_member_roles.
    """

    template_name = 'studio_suite/studio-info.html'

    def get(self, request, *args, **kwargs):
        """
        Description:
            Handle GET requests to initialize a form and render the studio information template.

        Returns:
            StudioInfoForm which allows studios to set up their account and studio_suite.
            Most notably, the unique studio_url_extension as a key for distinguishing
            studio's protected urls.
        
        TODO:
        Determin if the user already has a StudioInfo model and if so only serve them a form
        containing: bio, studio name, and new_member_roles.
        """

        return render(request, self.template_name, context={'StudioInfoForm': StudioInfoForm()})


    def post(self, request, *args, **kwargs):
        """
        Description:
            Handles POST requests to process the studio information form.

        Returns:
            Redirect to studio_home on successful form submission,
            or re-render the template with errors if the form is invalid.

        Security:
            Check Info Form Validity

            TODO
            - Check if the user already has a studio. If so, make sure only bio, studio name, 
              and new_member_roles are submitted.
        """

        studio_info_form = StudioInfoForm(request.POST)
        if studio_info_form.is_valid():
            studio_info = studio_info_form.save(commit=False)
            studio_info.linked_account = request.user
            studio_info.save()
            studio_url_extension = studio_info.url_extension
            return redirect(reverse('studio_home', kwargs={'studio_url_extension': studio_url_extension}))

        return render(request, self.template_name, context={'StudioInfoForm': studio_info_form})



class StudioView(View):
    """
    Description:
        Base view for studio-related functionality. Ensures the requesting user is logged in and
        owns the studio. Provides common data retrieval and context for studio views.

    Security:
        All studio management views inherite the following methods. Thefore,
        dispatch requires studio ownership and to be logged in.
    """

    @studio_ownership_required
    @method_decorator(login_required, name="dispatch")
    def dispatch(self, request, *args, **kwargs):
        """
        Description:
            Dispatch method to handle common functionality for studio views. Retrieves
            studio-related data and sets up context for rendering templates.

        Returns:
            Context data used for all pages.
            Most notable, the studio_url_extension is validated before responding.

        Security:
            TODO
            Remove user ID from object
            Remove studio ID from object
        """

        self.request = request  # Get requesting client data.
        self.user = request.user  # Get the user data from the request.
        self.studio_url_extension = kwargs.get('studio_url_extension')  # Get requested studio identifier.
        self.studio = get_object_or_404(StudioInfo, url_extension=self.studio_url_extension)

        # The following is data we want to be passed to every page.
        self.context = {
            'studio_url_extension': self.studio_url_extension,
            'studio': self.studio,
        }

        return super().dispatch(request, *args, **kwargs)



class StudioHomeView(StudioView):
    """
    Description:
        Home page for studio owners, the only notable functionality of this
        page is that it has all of it the page links for studio access and a
        link to change to the user_suite.
    
    Security:
        Dispatch security controls inherited from StudioView.
    """

    template_name = 'studio_suite/studio-home.html'

    def get(self, *args, **kwargs):
        """
        Description:
            Respond when a studio owner attempts access to their home page.

        Returns:
            Common context data and studio home page template.
        """

        return render(self.request, self.template_name, self.context)



class UpdateStudioInfoView(StudioView):
    """
    Description:
        Page where studio's can submit a form to update their bio, studio name
        or their defualt user role. Their unique studio extension shouldn't
        be changed because any users currently in the studio would effectively
        lose functionality until their made aware of the new extension.
    
    Security:
        - Dispatch security controls inherited from StudioView.
    
    Note:
        Depending on how frontend want's to implement the form submission fields,
        this could be easily served on the studio_suite home page.
    """

    template_name = 'studio_suite/update-studio-info.html'

    def update_context(self):
        """
        Description:
            Updates the base StudioView context with view specific data.
        """
        self.studio = get_object_or_404(StudioInfo, url_extension=self.studio_url_extension)
        StudioUpdateForm = self.get_form_class()

        self.context.update({
            'studio': self.studio,
            'StudioUpdateForm': StudioUpdateForm(),
        })


    def get_form_class(self):
        """
        Description:
            Modify's the StudioInfo form in numerous ways:
            1. Removes the ability to enter a new studio_url_extension.
               This maintains functionality for users.
            2. Overwrites the requirement for all fields to contain data.
               (Use case: Studios wont be forced to re-enter their studio
                name if they want to change the bio etc.)
            3. Returns the modified form with it's new parameters.
        """
        # Create a dynamic form class without the url_extension field
        class StudioUpdateForm(StudioInfoForm):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Set fields as not required
                self.fields['name'].required = False
                self.fields['bio'].required = False
                self.fields['new_member_role'].required = False

            def clean_name(self):
                name = self.cleaned_data.get('name')
                if name != "":
                    # Call the original clean_name method if it exists
                    return super().clean_name()
                return name

            def clean_bio(self):
                bio = self.cleaned_data.get('bio')
                if bio != "":
                    # Call the original clean_bio method if it exists
                    return super().clean_bio()
                return bio
            
            def clean_business_main_address(self):
                business_main_address = self.cleaned_data.get('business_main_address')
                if business_main_address != "":
                    # Call the original clean_business_main_address method if it exists
                    return super().clean_business_main_address()
                return business_main_address

            def clean_website_link(self):
                website_link = self.cleaned_data.get('website_link')
                if website_link != "":
                # Call the original clean_website_link method if it exists
                    return super().clean_website_link()
                return website_link

            def clean_timezone(self):
                timezone = self.cleaned_data.get('timezone')
                if timezone != "":
                # Call the original clean_timezone method if it exists
                    return super().clean_timezone()
                return timezone

            def clean_currency(self):
                currency = self.cleaned_data.get('currency')
                if currency != "":
                # Call the original clean_currency method if it exists
                    return super().clean_currency()
                return currency

            # If a clean function is created for the new member role, uncomment this:
            # def clean_new_member_role(self):
            #     new_member_role = self.cleaned_data.get('new_member_role')
            #     if new_member_role is not "":
            #         # Call the original clean_new_member_role method if it exists
            #         return super().clean_new_member_role()
            #     return new_member_role

            class Meta(StudioInfoForm.Meta):
                fields = [
                    'name',
                    'bio',
                    'new_member_role',
                    'business_main_address', #added main address
                    'website_link', #added website link
                    'timezone', #added timezone
                    'currency' #added currency
                ]

        # Dynamically remove the 'url_extension' field from the form
        del StudioUpdateForm.base_fields['url_extension']

        return StudioUpdateForm


    def get(self, *args, **kwargs):
        """
        Description:
            Serve the modified studio info form so that studio's can update their
            public info safely.
        """

        self.update_context()

        return render(self.request, self.template_name, self.context)


    def post(self, request, *args, **kwargs):
        """
        Description:
            Handles POST requests to process the studio information update form.

        Security:
            Check InfoUpdateForm for custom validity.
        """

        # Bind the form with the POST data
        StudioUpdateForm = self.get_form_class()(request.POST)  # Correct instantiation

        # Check if the form is valid
        if StudioUpdateForm.is_valid():
            # Retrieve the existing studio object from the database
            studio_info = StudioInfo.objects.get(linked_account=request.user)

            # Update the existing studio object with the new information only if it's not blank
            cleaned_data = StudioUpdateForm.cleaned_data
            if cleaned_data['name'] != "":
                studio_info.name = cleaned_data['name']
            if cleaned_data['bio'] != "":
                studio_info.bio = cleaned_data['bio']
            if cleaned_data['new_member_role'] != "":
                studio_info.new_member_role = cleaned_data['new_member_role']
            if cleaned_data['business_main_address'] != "":
                studio_info.business_main_address = cleaned_data['business_main_address']
            if cleaned_data['website_link'] != "":
                studio_info.website_link = cleaned_data['website_link']
            if cleaned_data['timezone'] != "":
                studio_info.timezone = cleaned_data['timezone']
            if cleaned_data['currency'] != "":
                studio_info.currency = cleaned_data['currency']
            
            # Save the updated studio object
            studio_info.save()

            self.update_context()

        else:
            # If the form is invalid, re-render the template with errors
            self.context['StudioUpdateForm'] = StudioUpdateForm

        return render(request, self.template_name, self.context)



class KilnManagementView(StudioView):
    """
    Description:
        View class for managing kilns in a studio. Extends StudioView to ensure
        proper authentication and studio ownership.
    
    Security:
        Dispatch security controls inherited from StudioView.
    """

    template_name = 'studio_suite/kiln-management.html'

    def update_context(self, fresh_CreateKilnForm: bool = None, fresh_CreateKilnRangeForm: bool = None):
        """
        Description:
            This context data is for both the GET and POST requests, instead of code duplication this
            serves to be a callable function to update the context when required.

        Note:
            When rendering it would display all "field required" for the opposite form
            of the submission. (Since there are two forms, it would error out the one
            not being submitted after a POST request)

            The bools:
                fresh_CreateKilnForm
                fresh_CreateKilnRangeForm

            Along with their logic in the POST function seem to fix this issue.

        Security:
            TODO
            Remove ID values from ranges and kilns
        """

        CreateKilnRangeForm = KilnRangeForm()
        CreateKilnForm = KilnManagementForm(studio=self.studio)
        ranges = KilnRange.objects.filter(studio=self.studio)
        kilns = KilnManagement.objects.filter(studio=self.studio)

        self.context.update({
            'CreateKilnRangeForm': CreateKilnRangeForm,
            'CreateKilnForm': CreateKilnForm,
            'ranges': ranges,
            'kilns': kilns
        })

        if fresh_CreateKilnForm:
            self.context['CreateKilnForm'] = KilnManagementForm()
        elif fresh_CreateKilnRangeForm:
            self.context['CreateKilnRangeForm'] = KilnRangeForm()


    def get(self, *args, **kwargs):
        """
        Description:
            Handle GET requests to render the kiln management template with forms and kiln data.

        Returns:
            Common context and kiln view template.

        Security:
            TODO
            Encrypt the prefilled forms ID values
        """

        self.update_context()

        for range_item in self.context['ranges']:
            range_item.delete_range_form = KilnRangeDeleteForm(initial={'delete_range_id': range_item.id})

        for kiln in self.context['kilns']:
            kiln.delete_kiln_form = KilnDeleteForm(initial={'delete_kiln_id': kiln.id})

        return render(self.request, self.template_name, self.context)


    def post(self, *args, **kwargs):
        """
        Description:
            Handles creating and destroying Kiln Ranges

        Returns:
            Dynamic form reloading based on success or failure of one
            of the two return forms on top of common context and kiln view template.

        Security:
            - Check All Incoming Form Data is Valid (Checks for required data
              and calls forms clean functions)
            TODO
            Decrypt the prefilled forms ID values (after encryption has been added of course)
            Move post validation checks to form clean functions.
        """

        CreateKilnRangeForm = KilnRangeForm(self.request.POST)
        fresh_CreateKilnRangeForm = False
        CreateKilnForm = KilnManagementForm(self.request.POST)
        fresh_CreateKilnForm = False

        # Deletion Requests
        if self.request.POST.get('delete_range_id'):
            delete_range_form = KilnRangeDeleteForm(self.request.POST)
            if delete_range_form.is_valid():
                kiln_range_to_delete = self.request.POST.get('delete_range_id')
                range_to_delete = get_object_or_404(KilnRange, pk=kiln_range_to_delete)
                range_to_delete.delete()

            return redirect(self.request.path_info)

        if self.request.POST.get('delete_kiln_id'):
            delete_kiln_form = KilnDeleteForm(self.request.POST)
            if delete_kiln_form.is_valid():
                kiln_id_to_delete = self.request.POST.get('delete_kiln_id')
                kiln_to_delete = get_object_or_404(KilnManagement, pk=kiln_id_to_delete)
                kiln_to_delete.delete()

            return redirect(self.request.path_info)

        # Creation Requests
        if CreateKilnRangeForm.is_valid():

            submitted_range_name = CreateKilnRangeForm.cleaned_data['range_name']
            existing_ranges = KilnRange.objects.filter(studio=self.studio, range_name=submitted_range_name).exists()

            if not existing_ranges:
                kiln_range = CreateKilnRangeForm.save(commit=False)
                kiln_range.studio = self.studio
                kiln_range.save()
                return redirect(self.request.path_info)
            else:
                CreateKilnRangeForm.add_error('range_name', 'A range with that name already exists for your studio.')
                fresh_CreateKilnForm = True

        elif CreateKilnForm.is_valid():
            # Save the form data to the KilnManagement model
            submitted_kiln_name = CreateKilnForm.cleaned_data['kiln_name']
            existing_kilns = KilnManagement.objects.filter(studio=self.studio, kiln_name=submitted_kiln_name).exists()

            if not existing_kilns:
                kiln_management = CreateKilnForm.save(commit=False)
                kiln_management.studio = self.studio
                kiln_management.save()

                return redirect(self.request.path_info)
            else:
                CreateKilnForm.add_error('kiln_name', 'A kiln with that name already exists for your studio.')
                fresh_CreateKilnRangeForm = True
        
        self.update_context(fresh_CreateKilnForm, fresh_CreateKilnRangeForm)

        return render(self.request, self.template_name, self.context)



class MemberManagementView(StudioView):
    """
    Description:
        View class for managing members within a studio. Extends StudioView to ensure
        proper authentication and studio ownership.

    Security:
        Inherits Studio View Dispatch Security

    """

    template_name = 'studio_suite/member-management.html'


    def get(self, *args, **kwargs):
        """
        Description:
            Handle GET requests to retrieve and display member information and role change forms.

        Returns:
            Member roles, an updated form to display each members role first in the
            drop down menu where role changes occur, and common context.
            Custom change role forms and delete member forms for each member.
        
        Security:
            Validate forms upons submission.
            TODO
            Remove member ID from formed members (and any other data that isnt needed on frontend)
            Encrypt member ID in delete_member_forms
        """

        members = MemberStudioRelationship.objects.filter(studio=self.studio)

        formed_members = []  # List to store tuples of member and associated forms

        for member in members:
            member_role = member.get_member_role()  # Fetch the role using the method
            role_form = MemberRoleChangeForm(initial={'member_role': member_role, 'member_id': member.id})
            delete_member_form = DeleteMemberForm(initial={'delete_member_id': member.id})
            formed_members.append((member, role_form, delete_member_form))  # Append tuple (member, role_form, delete_member_form)

        self.context.update({
            'formed_members': formed_members,  # Pass the list of tuples to the context
            'studio_url_extension': self.studio_url_extension,
        })

        return render(self.request, self.template_name, self.context)


    def post(self, *args, **kwargs):
        """
        Description:
            Handle POST requests to process member management actions, such as deleting members
            or changing member roles.

        Returns:
            Success or failure messages based on whether the action of changing the role or
            deleting a member relationship was completed without any issues.

        Security:
            Validate submitted forms.
            TODO
            Move post validations into the forms clean functions.
        """

        if 'delete_member_id' in self.request.POST:
            delete_member_form = DeleteMemberForm(self.request.POST)
            if delete_member_form.is_valid():
                member_id = delete_member_form.cleaned_data['delete_member_id']
                try:
                    member_relationship = MemberStudioRelationship.objects.get(id=member_id)
                    if member_relationship.studio == self.user.studioinfo:
                        member_relationship.delete()
                        messages.success(self.request, 'Member deleted successfully.')
                    else:
                        messages.error(self.request, 'You do not have permission to delete this member.')
                except MemberStudioRelationship.DoesNotExist:
                    messages.error(self.request, 'Member not found.')
            else:
                messages.error(self.request, 'Invalid form data for member deletion.')

        elif 'member_role' in self.request.POST:
            member_role_change_form = MemberRoleChangeForm(self.request.POST)
            if member_role_change_form.is_valid():
                member_id = self.request.POST.get('member_id')
                member_relationship = get_object_or_404(MemberStudioRelationship, id=member_id)
                
                # Ensure the member belongs to the current studio before changing the role
                if member_relationship.studio == self.request.user.studioinfo:
                    member_relationship.member_role = member_role_change_form.cleaned_data['member_role']
                    member_relationship.save()
                    messages.success(self.request, 'Member role updated successfully.')
                else:
                    messages.error(self.request, 'You do not have permission to change this member\'s role.')
            else:
                messages.error(self.request, 'Invalid form data for member role change.')

        return redirect('member_management', studio_url_extension=self.studio_url_extension)



class TimeslotManagementView(StudioView):
    """
    Description:
        View class for managing timeslots within a studio. Extends StudioView to ensure proper
        authentication and studio ownership.

    Unique Attributes:
        weekday_mapping (dict): A mapping of weekday integers to their corresponding names.
    
    Security:
        Inherits StudioView dispatch security mechanisms
    """

    template_name = 'studio_suite/timeslot-management.html'
    weekday_mapping = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday',
        }
    
    def update_context(self):
        """
        Description:
            Update the context with information required for rendering the timeslot management view.
            This context data is for both the GET and POST requests, instead of code duplication this
            serves to be a callable function to update the context when required.

        Security:
            TODO
            Remove Timeslot ID's from Timeslots.
        """
        is_kilns = KilnManagement.objects.filter(studio=self.studio).exists()
        timeslots = TimeslotManagement.objects.filter(studio=self.studio)
        #blackouts = TimeslotBlackout.objects.filter(studio=self.studio)
        form = TimeslotManagementForm(studio=self.studio)
        #blackout_form = TimeslotBlackoutForm()

        self.context.update({
            'is_kilns': is_kilns,
            'form': form,
            'timeslots': timeslots,
            #'blackout_form': blackout_form,
            #'blackouts': blackouts,
        })


    def get(self, *args, **kwargs):
        """
        Description:
            Handle GET requests to retrieve and display timeslot information and associated forms.

        Security:
            TODO
            Encrypt Timeslot ID's in the DeleteTimeslotForms
        """
        self.update_context()

        # Iterate through timeslots and create a DeleteTimeslotForm for each one
        for timeslot in self.context['timeslots']:
            # Prefill the form with the timeslot's ID
            delete_timeslot_form = DeleteTimeslotForm(initial={'delete_timeslot_id': timeslot.id})

            # Append the form to the timeslot
            timeslot.delete_timeslot_form = delete_timeslot_form

        return render(self.request, self.template_name, self.context)


    def post(self, *args, **kwargs):
        """
        Description:
            Handle POST requests to process timeslot management actions, such as creating or deleting timeslots.
            For an explanation of the Timeslot Collision Mechanism, please view the timeslot_collision_detection's
            doc comment.
        
        Returns:
            Either a collision warning or the updated context data and new timeslot record's data.
        
        Security:
            TODO
            Re-evaluate standing once further decisions have been made on the collision process.
        """

        self.update_context()

        if "create_timeslot" in self.request.POST:
            timeslot_form = TimeslotManagementForm(self.request.POST, studio=self.studio)
            if timeslot_form.is_valid():
                # Run Collision Test's and get collision messages:
                collisions_detected = self.timeslot_collision_detection(timeslot_form, self.studio)

                # If collision messages and their timeslots are returned:
                if collisions_detected:
                    # Add all information about collision to the context.
                    self.context['collisions_detected'] = collisions_detected
                    self.context['is_collision'] = True # Boolean Flag For Collisions.

                    # Add the information about the submitted form to the collision message,
                    # this way we can show direct comparisions for collisions.
                    self.context['submitted_form'] = {
                        'is_recurring': timeslot_form.cleaned_data['is_recurring'],
                        'start_date': timeslot_form.cleaned_data['start_date'],
                        'end_date': timeslot_form.cleaned_data['end_date'],
                        'recurring_weekdays': timeslot_form.cleaned_data['recurring_weekdays'],
                        'load_after_time': timeslot_form.cleaned_data['load_after_time']
                    }

                    # Re render the template with the collision messages.
                    return render(self.request, self.template_name, self.context)

                # If no collisions are detected, then save the new timeslot.
                else:
                    # Save the form.
                    timeslot_management = timeslot_form.save(commit=False)
                    timeslot_management.studio = self.studio # Set the studio in the form before saving.
                    timeslot_management.save()
                    # Now that the timeslot exists, relate the M2M recurring_weekdays to the timeslot.
                    timeslot_management.recurring_weekdays.set(timeslot_form.cleaned_data['recurring_weekdays'])

                    # Do a complete redirect to the page (Also clears the form).
                    return redirect('timeslot_management', studio_url_extension=self.studio_url_extension)
            else:
                # Add form errors to messages
                for field, errors in timeslot_form.errors.items():
                    for error in errors:
                        messages.error(self.request, f"{field}: {error}")

        if "delete_timeslot" in self.request.POST:
            print("here")

            # Get the delete form from the request data
            delete_form = DeleteTimeslotForm(self.request.POST)
            print(delete_form)
            # Verify if the delete form is valid
            if delete_form.is_valid():
                # Get the timeslot ID from the validated form data
                timeslot_id = delete_form.cleaned_data['delete_timeslot_id']
                try:
                    # Get the corresponding timeslot object
                    timeslot = TimeslotManagement.objects.get(id=timeslot_id)
                    
                    # Delete the timeslot
                    timeslot.delete()
                    return redirect(self.request.path_info)
                except TimeslotManagement.DoesNotExist:
                    # Handle if timeslot doesn't exist
                    messages.error(self.request, "Timeslot does not exist.")
                    return redirect(self.request.path_info)
            else:
                # Form validation failed, add error message to messages framework
                messages.error(self.request, "Form validation failed.")
                return redirect(self.request.path_info)
        
        ## Disabled
        # elif "create_blackout" in request.POST:
        #     blackout_form = TimeslotBlackoutForm(request.POST)
        #     if blackout_form.is_valid():
        #         blackout = blackout_form.save(commit=False)
        #         blackout.studio = studio

        #         timeslot_id = request.POST.get("timeslot_id")
        #         timeslot = TimeslotManagement.objects.get(id=timeslot_id)
        #         blackout.related_timeslot = timeslot
        #         blackout.save()
        #     else: # Temporary fix.
        #         messages.error(request, 'A Blackout End Date must be 24 hours after Blackout Start Date.')

        #     return redirect(request.path_info)

        #     # Do a complete redirect to the page (Also clears the form).
        
        # elif "delete_blackout" in request.POST:
        #     blackout_id = request.POST.get("blackout_id")
        #     try:
        #         blackout = TimeslotBlackout.objects.get(id=blackout_id)
        #         blackout.delete()
        #         return redirect(request.path_info)
        #     except TimeslotManagement.DoesNotExist:
        #         return redirect(request.path_info)
        

        return render(self.request, self.template_name, self.context)



    def weekday_formatting(self, recurring_weekday_input: list, date: date):
        """
        Description:
            Format weekdays for collision checking.

        Returns:
            list: Formatted list of weekdays.
        """

        # Empty weekday list or query set: use the date to calculate the weekday and make a list.
        if (not recurring_weekday_input) or (not recurring_weekday_input.exists()):
            date = datetime.strptime(str(date), '%Y-%m-%d').date()
            weekday_integers = [date.weekday()]
            weekdays_list = [self.weekday_mapping[integer] for integer in weekday_integers]
        # Else, convert the query set of weekday objects to a weekdays list.
        else:
            weekdays_list = [weekday.day for weekday in recurring_weekday_input]

        return weekdays_list


    def comparing_date_collisions(self, form_datetime: datetime, saved_datetime: datetime,):
        """
        Description:
            Check for collisions between date and start/end datetime.

        Returns:
            int: 1 if collision is detected.
        """

        if form_datetime >= saved_datetime:
            if (form_datetime - saved_datetime) <= timedelta(hours=23,minutes=59):
                return 1
        elif form_datetime < saved_datetime:
            if (saved_datetime - form_datetime) <= timedelta(hours=23, minutes=59):
                return 1

    def recurring_weekday_collisions(self, form_weekdays_list: list, saved_weekdays_list: list):
        """
        Description:
            Check for collisions between recurring weekdays.

        Returns:
            int: 1 if collision is detected.
        """

        for weekday in form_weekdays_list:
            if weekday in saved_weekdays_list:
                return 1

    def comparing_load_time_collisions(
            self,
            form_weekdays_list,
            form_load_after_time,
            saved_weekdays_list,
            saved_load_after_time
        ):

        """
        Description:
            Check for collisions between load_after_times.

        Returns:
            int: 1 if collision is detected.
        """

        # Create a dictionary to map weekdays to their respective indices
        weekday_index_mapping = {v: k for k, v in self.weekday_mapping.items()}

        # Iterate through each saved weekday
        for saved_weekday in saved_weekdays_list:
            saved_index = weekday_index_mapping.get(saved_weekday)

            if saved_index is not None:
                # Check if the form weekday is the day before
                form_index_before = (saved_index - 1) % 7
                if self.weekday_mapping[form_index_before] in form_weekdays_list:
                    if form_load_after_time > saved_load_after_time:
                        return 1

                # Check if the form weekday is the day after
                form_index_after = (saved_index + 1) % 7
                if self.weekday_mapping[form_index_after] in form_weekdays_list:
                    if form_load_after_time < saved_load_after_time:
                        return 1


    def timeslot_collision_detection(self, form: TimeslotManagementForm, studio):
        """
        Description:
            Detect collisions between a submitted timeslot and existing timeslots in a kiln.
            This function checks for collisions between a timeslot submitted via a form and
            existing timeslots in a specific kiln for each specific studio.
            It considers various collision scenarios, including date overlaps, recurring weekdays,
            and load_after_time conflicts (Load times within 24 hours of each other).
        
        High Level Explanation:
            For all saved Timeslots with the same Kiln as the New Submitted Timeslot:
                Check for all possible collision scenarioes where necessary:
                    Some Examples:
                        Start Dates Cant Collide
                        End Dates Cant Collide
                        Start and End Dates Cant Collide
                        Recurring Weekdays Cant Collide
                        If single date timeslots happens during a recurring timeslot,
                            the weekday cant collide and load time must be greater than
                            24 hours.
                        Load times must be more than 24 hours apart.
            All generated warnings are then passed back to the frontend.

            This is all done using conditional statements to reduce operations and checks down
            only to the possible collision scenarios based on the recurrence type.

        Returns:
            collisions_detected (list): A list of collisions detected, where each collision is
            represented as a tuple containing collision warnings and the associated timeslot.
            The collision warnings are strings describing the type of collision detected.
        """

        # Get all the new timeslot information from the submitted form.
        form_studio = studio
        form_kiln = form.cleaned_data['kiln']
        form_is_recurring = form.cleaned_data['is_recurring']
        form_recurring_weekdays = form.cleaned_data['recurring_weekdays']
        form_end_date = form.cleaned_data['end_date']
        form_start_date = form.cleaned_data['start_date']
        form_load_after_time = form.cleaned_data['load_after_time']
        form_weekdays_list = self.weekday_formatting(form_recurring_weekdays, form_start_date)
        collisions_detected = []
        collision_message = {
            # Do not re-number the keys, if you create a new collision rule, add a new key for it.
            # I plan to redo these messages to make them much more specific.
            0:'Submitted Timeslots Date (or Start Date) is less than 24 hours from the following Timeslots Date (or Start Date).',
            1:'Submitted Timeslots End Date is less than 24 hours from the following Timeslots Date.',
            2:'Submitted Timeslots Recurring Weekdays will overlap the following Timeslots Date.',
            3:'Submitted Timeslots Recurring Weekdays will overlap (some of) the following Timeslots Recurring Weekdays.',
            4:'Submitted Timeslots Date (or Start Date) is less than 24 hours from the following Timeslots End Date.',
            5:'Submitted Timeslots Date overlaps the following Timeslots Recurring Weekdays.',
            6:'Submitted Timeslots End Date is less than 24 hours from the following Timeslots Start Date.',
            7:'Submitted Timeslots Load After Time is less than 24 hours from the following Timeslots Load After Time (Is within 24 hours of another timeslots load after time).'
        }

        # Format Forms Start and End Time
        form_start_datetime = datetime.combine(form_start_date, form_load_after_time)
        if form_end_date:
            form_end_datetime = datetime.combine(form_end_date, form_load_after_time)


        # Collision detection
        kiln_timeslots = TimeslotManagement.objects.filter(studio=form_studio, kiln=form_kiln)
        for saved_timeslot in kiln_timeslots:

            collision_warnings = []

            # Turn Stored Query Set To List
            saved_recurring_weekdays = saved_timeslot.recurring_weekdays.all()
            saved_weekdays_list = self.weekday_formatting(saved_recurring_weekdays, saved_timeslot.start_date)
            saved_load_after_time = saved_timeslot.load_after_time

            # Format saved_timeslots start and end_times for collision checking
            saved_start_datetime = datetime.combine(saved_timeslot.start_date, saved_timeslot.load_after_time)
            if saved_timeslot.end_date:
                saved_end_datetime = datetime.combine(saved_timeslot.end_date, saved_timeslot.load_after_time)


            # General Rule: Start dates can't collide with one another.
            if self.comparing_date_collisions(form_start_datetime, saved_start_datetime):
                collision_warnings.append(collision_message[0])


            if saved_timeslot.is_recurring == 0: # Saved Never Recurres

                if form_is_recurring == 1: # Form Recurring Temporarily
                    # Forms end date must not collide with saved start date.
                    if self.comparing_date_collisions(form_end_datetime, saved_start_datetime):
                        collision_warnings.append(collision_message[1])

                    # If saved never recurring date is during the forms temporary date range
                        # weekdays can't collide.
                        # 24hrs loads can't collide
                    if saved_start_datetime > form_start_datetime or saved_start_datetime < form_end_datetime:
                        if self.recurring_weekday_collisions(form_weekdays_list, saved_weekdays_list):
                            collision_warnings.append(collision_message[2])
                        if self.comparing_load_time_collisions(
                                form_weekdays_list,
                                form_load_after_time,
                                saved_weekdays_list,
                                saved_load_after_time
                            ):
                            collision_warnings.append(collision_message[7])

                elif form_is_recurring == 2: # Form Recurring Forever

                    # If saved never recurring date is after forms start date.
                        # weekdays can't collide.
                        # 24hrs loads can't collide.
                    if saved_start_datetime > form_start_datetime:
                        if self.recurring_weekday_collisions(form_weekdays_list, saved_weekdays_list):
                            collision_warnings.append(collision_message[2])
                        if self.comparing_load_time_collisions(
                                form_weekdays_list,
                                form_load_after_time,
                                saved_weekdays_list,
                                saved_load_after_time
                            ):
                            collision_warnings.append(collision_message[7])

            elif saved_timeslot.is_recurring == 1:

                if form_is_recurring == 0:
                    # Forms start_date can't collide with saved end_date
                    if self.comparing_date_collisions(form_start_datetime, saved_end_datetime):
                        collision_warnings.append(collision_message[4])
                        
                    # If forms never recurring start date is in saved temp recurring date range, weekdays can't collide.
                    if form_start_datetime > saved_start_datetime and form_start_datetime < saved_end_datetime:
                        if self.recurring_weekday_collisions(form_weekdays_list, saved_weekdays_list):
                            collision_warnings.append(collision_message[5])
                        if self.comparing_load_time_collisions(
                                form_weekdays_list,
                                form_load_after_time,
                                saved_weekdays_list,
                                saved_load_after_time
                            ):
                            collision_warnings.append(collision_message[7])


                elif form_is_recurring == 1:
                    # Forms start can't collide with saved end date
                    if self.comparing_date_collisions(form_start_datetime, saved_end_datetime):
                        collision_warnings.append(collision_message[4])
                    # Forms end date can't collide with saved start date
                    if self.comparing_date_collisions(form_end_datetime, saved_end_datetime):
                        collision_warnings.append(collision_message[6])
                    # If form start date is after saved start date or forms end date is before saved end date
                        # weekdays cant collide
                        # load_after_times can't collide
                    if form_start_datetime > saved_start_datetime or form_end_datetime > saved_end_datetime:
                        if self.recurring_weekday_collisions(form_weekdays_list, saved_weekdays_list):
                            collision_warnings.append(collision_message[3])
                        if self.comparing_load_time_collisions(
                                form_weekdays_list,
                                form_load_after_time,
                                saved_weekdays_list,
                                saved_load_after_time
                            ):
                            collision_warnings.append(collision_message[7])

                elif form_is_recurring == 2:
                    # Forms start date cant collide with saved end date
                    if self.comparing_date_collisions(form_start_datetime, saved_end_datetime):
                        collision_warnings.append(collision_message[4])
                    # If forms start date is after saved start date but before saved end date
                        # weekdays can't collide.
                        # 24hrs loads can't collide.
                    if form_start_datetime > saved_start_datetime and form_start_datetime < saved_end_datetime:
                        if self.recurring_weekday_collisions(form_weekdays_list, saved_weekdays_list):
                            collision_warnings.append(collision_message[3])
                        if self.comparing_load_time_collisions(
                                form_weekdays_list,
                                form_load_after_time,
                                saved_weekdays_list,
                                saved_load_after_time
                            ):
                            collision_warnings.append(collision_message[7])

            elif saved_timeslot.is_recurring == 2:
                if form_is_recurring == 0:
                    # If forms start date is after saved start date
                        # weekdays can't collide.
                        # 24hrs loads can't collide.
                    if form_start_datetime > saved_start_datetime:
                        if self.recurring_weekday_collisions(form_weekdays_list, saved_weekdays_list):
                            collision_warnings.append(collision_message[5])
                        if self.comparing_load_time_collisions(
                                form_weekdays_list,
                                form_load_after_time,
                                saved_weekdays_list,
                                saved_load_after_time
                            ):
                            collision_warnings.append(collision_message[7])

                elif form_is_recurring == 1:
                    # Form end date can't collide with saved start date
                    if self.comparing_date_collisions(form_end_datetime, saved_start_datetime):
                        collision_warnings.append(collision_message[6])
                    # If form start date or end date is after saved start date
                        # weekday's can't collide
                        # 24hrs loads can't collide.
                    if form_start_datetime > saved_start_datetime or form_end_datetime > saved_start_datetime:
                        if self.recurring_weekday_collisions(form_weekdays_list, saved_weekdays_list):
                            collision_warnings.append(collision_message[3])

                        if self.comparing_load_time_collisions(
                                form_weekdays_list,
                                form_load_after_time,
                                saved_weekdays_list,
                                saved_load_after_time
                            ):
                            collision_warnings.append(collision_message[7])
                    
                elif form_is_recurring == 2:
                    # Form weekdays can't collide
                    # 24hrs loads can't collide.
                    if self.recurring_weekday_collisions(form_weekdays_list, saved_weekdays_list):
                        collision_warnings.append(collision_message[3])
                    if self.comparing_load_time_collisions(
                            form_weekdays_list,
                            form_load_after_time,
                            saved_weekdays_list,
                            saved_load_after_time
                        ):
                        collision_warnings.append(collision_message[7])

            # If there are collisions, associate them all to the timeslot.
            if collision_warnings:
                collisions_detected.append([collision_warnings, saved_timeslot])
        
        return collisions_detected  
