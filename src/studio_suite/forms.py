"""
Custom forms served in relation to studio information gathering.
"""

import re
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from datetime import timedelta
from django import forms
from .models import (
    StudioInfo,
    KilnManagement,
    KilnRange,
    TimeslotManagement,
    Weekday,
    TimeslotBlackout,
    MemberStudioRelationship,
)



class StudioInfoForm(forms.ModelForm):
    """
    Description:
        This form is used for creating or updating StudioInfo objects based on the 'StudioInfo' model.
        It provides fields for the studio's name, unique URL extension, and bio, along with custom
        validation logic to ensure data integrity and security.
    
    Related Model:
        StudioInfo

    Security:

    """

    class Meta:
        """
        Description:
            The model class to which this form is associated.
        """

        model = StudioInfo
        fields = [
            'name',
            'url_extension',
            'bio',
            'new_member_role',
            'business_main_address', #added address
            'website_link', #added link
            'timezone', #added timezone
            'currency' #added currency
            ]

    url_extension = forms.CharField(
        label="Example: This will be your unique signup link -> handleit.app/accounts/member-signup/",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'UNIQUE url_extension'}),
    )

    def clean_business_main_address(self):
        """
        Description:
        Custom validation method to verify the format of the business main address.
        """
        business_main_address = self.cleaned_data['business_main_address']

        # Basic check to ensure it's not empty
        if not business_main_address:
            raise forms.ValidationError("Business main address cannot be empty.")

        # Check if it contains at least one number (all addresses must have at least one number to be a valid address)
        if not any(char.isdigit() for char in business_main_address):
            raise forms.ValidationError("Business main address must contain at least one number.")

        return business_main_address

    def clean_timezone(self):
        """
        Custom validation method to verify the selected timezone.
        """

        timezone = self.cleaned_data['timezone']

        # List of valid timezones
        valid_timezones = [choice[0] for choice in StudioInfo.TIMEZONE_CHOICES]

        # Check if the selected timezone is in the list of valid options
        if timezone not in valid_timezones:
            raise forms.ValidationError("Please select a valid timezone.")

        return timezone

    def clean_currency(self):
        """
        Description:
        Custom validation method to verify the selected currency.
        """

        currency = self.cleaned_data['currency']

        # List of valid currencies
        valid_currencies = [choice[0] for choice in StudioInfo.CURRENCY_CHOICES]
        # Check if the selected currency is in the list of valid options
        if currency not in valid_currencies:
            raise forms.ValidationError("Please select a valid currency.")

        return currency

    def clean_url_extension(self):
        """
        Description:
            Custom validation method to check allowed characters in the URL extension.
        """

        url_extension = self.cleaned_data['url_extension']

        # Use a regular expression to check for allowed characters (a-zA-Z)
        if not re.match("^[a-zA-Z-]+$", url_extension):
            raise forms.ValidationError("url_extension can only contain letters (a through z) and hyphens (-).")

        return url_extension


    def clean_name(self):
        """
        Description:
            Custom validation method to verify the studio name.
        """

        name = self.cleaned_data['name']

        # Verify the name field data - Implement Security Checks.
        if not name.replace(" ", "").isalpha():  # Remove Spaces and Verify Alphabet Chars Only.
            raise forms.ValidationError("Name must contain only letters and spaces.")

        return name


    def clean_bio(self):
        """
        Description:
            Custom validation method to check for potential script content in the bio field.
        """

        bio = self.cleaned_data['bio']

        # Check the bio field data - Implement Security Checks.
        if '<script>' in bio:
            raise forms.ValidationError("Bio cannot contain scripts.")

        return bio


class KilnRangeForm(forms.ModelForm):
    """
    Description:
        A form for creating and updating kiln management entries.
        This form is used for creating or updating kiln management entries. It allows users to specify
        various attributes related to kilns, including the kiln name, make, model, size, and maximum
        temperature.

    Related Model:
        KilnRange

    Security:
    """
    class Meta:
        """
        Description:
        """
        model = KilnRange
        fields = ['range_name', 'min_temp', 'max_temp']

    def __init__(self, *args, **kwargs):
        """
        Description:
        """
        super(KilnRangeForm, self).__init__(*args, **kwargs)
        # Customize the widgets or any additional attributes if needed
        self.fields['min_temp'].widget = forms.Select(choices=KilnRange.TEMP_CHOICES)
        self.fields['max_temp'].widget = forms.Select(choices=KilnRange.TEMP_CHOICES)
    
    
class KilnRangeDeleteForm(forms.Form):
    """
    Description:
        A hidden form for collecting ID's of Kiln Ranges intended to be deleted.

    Related Model:
        KilnRange

    Security:
    """
    delete_range_id = forms.IntegerField(widget=forms.HiddenInput())



class KilnManagementForm(forms.ModelForm):
    """
    Description:
        A form for creating and updating kiln management entries.
        This form is used for creating or updating kiln management entries. It allows users to specify
        various attributes related to kilns, including the kiln name, make, model, size, and maximum
        temperature.

    Related Model:
        KilnManagement

    Security:
    """

    class Meta:
        model = KilnManagement
        fields = [
            'kiln_name',
            'kiln_make',
            'kiln_model',
            'kiln_size',
            'kiln_max_temp',
            'kiln_range',  # Add this field for the KilnRange relation
        ]
        labels = {
            'kiln_name': 'Unique Kiln Name',
            'kiln_make': 'Kiln Make',
            'kiln_model': 'Kiln Model',
            'kiln_size': 'Kiln Size',
            'kiln_max_temp': 'Kiln Maximum Temperature',
            'kiln_range': 'Kiln Range',
        }

    def __init__(self, *args, **kwargs):

        studio = kwargs.pop('studio', None)  # Get the user from the form's kwargs if needed
        super(KilnManagementForm, self).__init__(*args, **kwargs)

        # Customize the queryset for the kiln field based on your requirements
        if studio:
            self.fields['kiln_range'].queryset = KilnRange.objects.filter(studio=studio)



class KilnDeleteForm(forms.Form):
    """
    Description:
        A hidden form for collecting the ID of Kilns intended to be deleted.

    Related Model:
        KilnManagement

    Security:
    """
    delete_kiln_id = forms.IntegerField(widget=forms.HiddenInput())



class TimeslotManagementForm(forms.ModelForm):
    """
    Description:
        This form is used for creating or updating timeslot management,
        entries associated with kilns. It provides, fields for specifying various
        attributes such as kiln selection, recurrence settings, start and end dates,
        load after time, and special remarks.
    
    Related Model:
        

    Security:
    """

    recurrence_frequency = forms.ChoiceField(
        label='Occurs',
        required=False,
        choices=TimeslotManagement.RECURRENCE_FREQUENCY_CHOICES,
    )

    recurring_weekdays = forms.ModelMultipleChoiceField(
        label = '',
        required=False,
        queryset=Weekday.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the TimeslotManagementForm with optional customization.

        This method allows for custom initialization and configuration of the form.
        In particular, it checks for the 'studio' keyword argument in 'kwargs'and,
        if provided, customizes the 'kiln' field's queryset based on the 'studio' value.
        """

        studio = kwargs.pop('studio', None)  # Get the user from the form's kwargs if needed
        super(TimeslotManagementForm, self).__init__(*args, **kwargs)

        # Customize the queryset for the kiln field based on your requirements
        if studio:
            self.fields['kiln'].queryset = KilnManagement.objects.filter(studio=studio)



    class Meta:
        """
        Description:
            Defines the model and form fields used, as well as labels and widgets for rendering.
        """

        model = TimeslotManagement
        fields = [
            'kiln',
            'min_role_required',
            'is_recurring',
            'recurrence_frequency',
            'recurring_weekdays',
            'start_date',
            'end_date',
            'load_after_time',
            'notes',
        ]

        labels = {
            'kiln': 'Kiln',
            'min_role_required': 'Required Role',
            'is_recurring': 'Repeat',
            'recurrence_frequency': 'Occurs',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'load_after_time': 'Load After Time',
            'notes': 'Special Remarks',
        }

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'load_after_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'cols': 26, 'rows': 1})
        }


    def clean(self):
        """
        Description:
            Clean and validate the form data.
            This method performs additional validation and cleaning of form data to ensure it adheres to
            business rules and constraints. It handles special cases for recurring bookings, checks for
            valid start and end dates, and provides custom error messages for better user feedback.
        """

        cleaned_data = super().clean()
        is_recurring = cleaned_data.get('is_recurring')
        recurrence_frequency = cleaned_data.get('recurrence_frequency')
        recurring_weekdays = cleaned_data.get('recurring_weekdays')

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Note: needed for checking start_dates and end_date not for storing Weekdays.
        weekday_mapping = {
                0: 'Monday',
                1: 'Tuesday',
                2: 'Wednesday',
                3: 'Thursday',
                4: 'Friday',
                5: 'Saturday',
                6: 'Sunday',
            }

        if is_recurring == 0: # Never

            cleaned_data['recurrence_frequency'] = None
            cleaned_data['end_date'] = None
            cleaned_data['recurring_weekdays'] = []

        elif is_recurring == 1: # Temporarily

            if not recurrence_frequency:
                self.add_error('recurrence_frequency', 'Required for recurring bookings.')
            if not recurring_weekdays:
                self.add_error('recurring_weekdays', 'Required for recurring bookings.')

            if not end_date:
                self.add_error('end_date', 'Required for recurring bookings.')

            if end_date and recurring_weekdays:
                form_weekdays_list = [weekday.day for weekday in recurring_weekdays]
                startdate_weekday = weekday_mapping[start_date.weekday()]
                if startdate_weekday not in form_weekdays_list:
                    self.add_error('start_date', f"Start date must be on a selected recurring weekday {form_weekdays_list}. Current '{startdate_weekday}'.")

                enddate_weekday = weekday_mapping[end_date.weekday()]
                if enddate_weekday not in form_weekdays_list:
                    self.add_error('end_date', f"End date must be on a selected recurring weekday {form_weekdays_list}. Current '{enddate_weekday}'.")


        elif is_recurring == 2: # Forever
            cleaned_data['end_date'] = None
            form_weekdays_list = [weekday.day for weekday in recurring_weekdays]

            if not recurrence_frequency:
                self.add_error('recurrence_frequency', 'Required for recurring bookings.')

            startdate_weekday = weekday_mapping[start_date.weekday()]
            if startdate_weekday not in form_weekdays_list:
                self.add_error('start_date', f"Start date must be on a selected recurring weekday {form_weekdays_list}. Current '{startdate_weekday}'.")

        if start_date and end_date:
            if end_date <= start_date:
                self.add_error('end_date', 'End date must be after the start date.')

        return cleaned_data



class DeleteTimeslotForm(forms.Form):
    """
    Description:
        Allows studio's to delete their timeslot rules.

    Collects:

    Security:
    """

    delete_timeslot_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'readonly': 'readonly'}))



class TimeslotBlackoutForm(forms.ModelForm):
    """
    Description:

    Collects:

    Security:
    """
    class Meta:
        model = TimeslotBlackout
        fields = [
            'blackout_start_datetime',
            'blackout_end_datetime',
            'blackout_reason'
        ]

        labels = {
            'blackout_start_datetime': 'Start Blackout',
            'blackout_end_datetime': 'End Blackout',
            'blackout_reason': 'Reason',
        }

        widgets = {
            'blackout_start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'blackout_end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'blackout_reason': forms.Textarea(attrs={'cols': 26, 'rows': 1})
        }

    def clean(self):
        """
        Description:
        """
        # Since these forms are loaded to the timeslot id and not statically
        # displaying form errors doesnt seem to work as they're redirected over.

        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('blackout_start_datetime')
        end_datetime = cleaned_data.get('blackout_end_datetime')

        if start_datetime and end_datetime:
            time_difference = end_datetime - start_datetime

            # Check if the time difference is less than 24 hours
            if time_difference < timedelta(hours=24):
                raise forms.ValidationError('End date must be 24 hours after the start date.')

        return cleaned_data



class MemberRoleChangeForm(forms.ModelForm):
    """
    Description:
        Form for changing the role of a member within a studio.

    Collects:
        Drop Down: New Desired Member Role
        Hidden: Related Member ID (Hidden)

    Security:
        Cleaners:
        Hidden Data Encryption:
    """

    member_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        """ """
        model = MemberStudioRelationship
        fields = ['member_role']
        labels = {
            'member_role': '',  # Setting the label to an empty string
        }



class DeleteMemberForm(forms.Form):
    """
    Description:
        Form for deleting a member within a studio. Collects the members ID to remove
        their studio relationship from the MemberStudioRelationship table.
    
    Collects:
        Hidden: Related Member ID

    Security:
        Cleaners:
        Hidden Data Encryption:
    """

    delete_member_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'readonly':'readonly'}))