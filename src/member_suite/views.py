"""
Member Views for Studio Interaction

These views are specifically designed for members' access to interact with the studio features. 
They serve as counterparts to studio_suite views, allowing members to engage with various 
functionalities. For instance, if a studio enables bookings, members can view and interact with
the booking system when logged into their studio account.
"""

from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from studio_suite.models import StudioInfo, MemberStudioRelationship, TimeslotManagement
from .models import BookingManagement
from .forms import BookKilnForm, UnbookKilnForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from app.decorators import member_group_required
from django.contrib import messages

from datetime import datetime, timedelta


class MemberView(View):
    """
    Description:
        Base view class for members of a studio. Ensures that the user is logged in and has signed up as a member
        of the studio. Handles common functionality such as fetching studio information and checking ownership.
    
    Security:
        Dispatch Requires Login and Member Group Decorator    
    """

    @member_group_required # Has signed up as a member of the studio.
    @method_decorator(login_required, name="dispatch") # Check the user is logged in.
    def dispatch(self, request, *args, **kwargs):
        """
        Description:
            Dispatch method to handle incoming requests for member views.

        Returns:
            Common context required for the functionality and general protection of
            member_suite Views.
        
        Security:
        TODO:
        - Remove Users ID From Context
        - Remove Studio UUID From Context
        """

        self.request = request  # Get requesting client data.
        self.user = request.user  # Get the user data from the request.
        self.studio_url_extension = kwargs.get('studio_url_extension')  # Get requested studio identifier.
        self.studio = get_object_or_404(StudioInfo, url_extension=self.studio_url_extension)
        self.is_owner = request.user == self.studio.linked_account  # Check if user has access to studio_suite.

        # The following is data we want to be passed to every page update.
        self.context = {
            'studio_url_extension': self.studio_url_extension,
            'studio': self.studio,
            'is_owner': self.is_owner,
        }

        return super().dispatch(request, *args, **kwargs)



class MemberHomeView(MemberView):
    """
    Description:
        View class for the member's home page. Extends MemberView to ensure the user is a logged-in member
        and fetches common data for member views.

    Security:
        Dispatch Requires Login and Member Group Decorator
    """

    template_name = 'member_suite/member-home.html'

    def get(self, *args, **kwargs):
        """
        Description:
            Handles GET requests for the member's home page. Fetches the studios associated with the logged-in member.

        Returns:
            Common context and the member studio relationships (which are likely to move to the Profile Page).

        Security:
            TODO
            Remove Studio ID and Member ID's from user_studios objects
        """

        # Temp: Show all studios the user is associated with.
        user_studios = MemberStudioRelationship.objects.filter(member=self.user)
        
        self.context.update({
            'user_studios': user_studios,
        })

        return render(self.request, self.template_name, self.context)



class BookAKilnView(MemberView):
    """
    Description:
        View class for booking kiln timeslots. Extends MemberView to ensure the user is a logged-in member
        and fetches common data for member views.
    
    Security:
        Dispatch Requires Login and Member Group Decorator
    """

    template_name = 'member_suite/book-a-kiln.html'

    def get(self, *args, **kwargs):
        """
        Description:
            Handles GET requests for the kiln booking page. Fetches available timeslots for the next 90 days
            and related booking information for display.

        Returns:
            Required information for display bookable or non bookable timeslots on top of the common context.
        
        Security:
            TODO:
            Remove ID's from user_bookings & upcoming timeslots
        """

        # Generate a list of the next 90 days.
        next_90_days = self.get_next_90_days()

        # Get all of this studios existing bookings for the next 90 days for all users.
        bookings_within_90_days = BookingManagement.objects.filter(
            studio=self.studio,
            booking_date__range=[next_90_days[0], next_90_days[-1]]
        )

        # Create a list of all bookable timeslots, checked against booked timeslots for validity.
        upcoming_timeslots = self.get_upcoming_bookings(self.studio, next_90_days, self.user, self.is_owner, bookings_within_90_days)

        # Get all of this users bookings so that they may unbook them if they choose.
        users_bookings = self.get_users_bookings()


        self.context.update({
            'next_90_days': next_90_days,
            'upcoming_timeslots': upcoming_timeslots,
            'users_bookings': users_bookings,
        })

        return render(self.request, self.template_name, self.context)


    def post(self, *args, **kwargs):
        """
        Description:
            Handles POST requests for the kiln booking page. Processes kiln booking and unbooking requests.
            Also manages all formatting of data required for booking and checking validity of requests.

        Returns:
            Messages regarding the success of booking.
        
        Security:
            TODO
            Remove forced datetime (try/excepts) formats once the forms clean function has been implemented.
            Remove other crossover checks once the form clean function is implemented.
        """

        if 'book_timeslot' in self.request.POST:
            timeslot_id = self.request.POST['book_timeslot']
            day = self.request.POST['day']
            booking_form = BookKilnForm(self.request.POST)

            if booking_form.is_valid():
                timeslot_id = booking_form.cleaned_data.get('book_timeslot')
                day = booking_form.cleaned_data.get('day')
            
                # Force the datetime format
                try:
                    day = datetime.strptime(day, "%Y-%m-%d")
                except ValueError:
                    return HttpResponseBadRequest("Invalid date format")
                
                timeslot = TimeslotManagement.objects.get(studio=self.studio, id=timeslot_id)

                # Set the booking_date to the selected day and the load_after_time of the timeslot
                booking_date = datetime.combine(day, timeslot.load_after_time)

                # Check if the timeslot is already booked on the selected day
                if BookingManagement.objects.filter(timeslot=timeslot, booking_date=booking_date).exists():
                    # Timeslot is already booked, add a failure message and don't save the booking.
                    messages.error(self.request, "Timeslot is already booked on this day.")
                else: # Timeslot is free to book
                    # Book and provide a success message.
                    BookingManagement.objects.create(
                        studio=self.studio,
                        member=self.request.user,
                        timeslot=timeslot,
                        booking_date=booking_date
                    )

                    messages.success(self.request, "Booking successful!")

        if 'unbook_timeslot' in self.request.POST:
            unbook_form = UnbookKilnForm(self.request.POST)
            if unbook_form.is_valid():

                timeslot_id = unbook_form.cleaned_data.get('unbook_timeslot')
                unbook_date_str = unbook_form.cleaned_data.get('unbook_date')

                try:
                    unbook_date = datetime.strptime(unbook_date_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    messages.error(self.request, "Invalid date format")
                    return redirect('book_a_kiln', studio_url_extension=self.studio_url_extension)

                if timeslot_id is not None:
                    booking_to_unbook = get_object_or_404(
                        BookingManagement,
                        timeslot__id=timeslot_id,
                        member=self.request.user,
                        booking_date=unbook_date
                    )

                    booking_to_unbook.delete()
                    messages.success(self.request, "Booking canceled successfully!")

        # Redirect to the booking page or any other appropriate page
        return redirect('book_a_kiln', studio_url_extension=self.studio_url_extension)


    def get_next_90_days(self):
        """
        Description:
            Fetches the next 90 days from the current date.

        Returns:
            next_90_days (list): A list of datetime objects representing the next 90 days.
        """

        # Generate a list of datetime objects for the next 90 days
        start_date = datetime.now()
        next_90_days = [(start_date + timedelta(days=day)).date() for day in range(90)]

        return next_90_days


    def get_users_bookings(self):
        """
        Description:
            Gets all of the users upcoming bookings, pulls the data from that timeslots,
            places it into an undeditable unbooking form, then appends that form to the
            timeslots.

        Returns:
            users_bookings (list): containing all of the users bookings for that specific
            studio as well as a prefilled uneditable hidden form which allows them to unbook it.
        """

        users_bookings = BookingManagement.objects.filter(member=self.user, studio=self.studio)
        # for booking in users_bookings (apply uneditable unbook form)
        
        for booking in users_bookings:
            unbook_form = UnbookKilnForm(
                initial={
                    'unbook_timeslot': booking.timeslot.id,
                    'unbook_date': booking.booking_date.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            booking.unbook_form = unbook_form
        return users_bookings


    def get_upcoming_bookings(self, studio: StudioInfo, date_list: list, user, is_owner, bookings_within_90_days):
        """
        Description:
            Relates days to bookable timeslots for display.

        Returns:
            dict: A dictionary where keys are dates and values are lists of bookable timeslots for each date.
        """

        # Fetch all timeslots associated with the studio
        studio_timeslots = TimeslotManagement.objects.filter(studio=studio)

        # Initialize an empty dictionary to store bookable timeslots for each date
        upcoming_timeslots = {key: [] for key in date_list}

        # Check if the user is not the owner, and get the user's role and indexed role values
        if not is_owner:
            member_role = MemberStudioRelationship.objects.get(member=user, studio=studio).get_member_role()
            indexed_roles = {tpl[0]: i for i, tpl in enumerate(MemberStudioRelationship.MEMBER_ROLE_CHOICES)}

        # Iterate through each timeslot and relate it to the given dates
        for timeslot in studio_timeslots:
            # Check if the user is the owner or has sufficient role permissions
            if is_owner or indexed_roles.get(member_role) >= indexed_roles.get(timeslot.min_role_required):
                for day in date_list:
                    recurring_weekdays = [day.day for day in timeslot.recurring_weekdays.all()]
                    is_booked = self.check_timeslot_booked(timeslot, day, bookings_within_90_days)

                    # Check if the timeslot is not recurring and starts on the specified day
                    if timeslot.end_date is None:
                        if timeslot.is_recurring == False and timeslot.start_date == day:
                            timeslot_info = {'timeslot': timeslot, 'is_booked': is_booked}
                            upcoming_timeslots[day].append(timeslot_info)

                        # Check if the timeslot is recurring and the day falls within the range
                        elif timeslot.is_recurring and timeslot.start_date <= day:
                            if day.strftime("%A") in recurring_weekdays:
                                timeslot_info = {'timeslot': timeslot, 'is_booked': is_booked}
                                upcoming_timeslots[day].append(timeslot_info)

                    # Check if the day falls within the range of a recurring timeslot with an end date      
                    elif timeslot.start_date <= day <= timeslot.end_date:
                        if day.strftime("%A") in recurring_weekdays:
                            timeslot_info = {'timeslot': timeslot, 'is_booked': is_booked}
                            upcoming_timeslots[day].append(timeslot_info)
        
        self.append_booking_forms(upcoming_timeslots)

        # Return the dictionary of bookable timeslots for each date
        return upcoming_timeslots

    def check_timeslot_booked(self, timeslot, day, bookings_within_90_days):
        """
        Description:
            Checks if a timeslot is booked on a specific day.

        Returns:
            bool: True if the timeslot is booked on the given day, False otherwise.
        """
        
        for booking in bookings_within_90_days:
            # Check if the booking corresponds to the provided timeslot and day
            if booking.timeslot == timeslot and booking.booking_date.date() == day:
                return True
        return False
    
    
    def append_booking_forms(self, upcoming_timeslots):
        """
        Description:
            Add custom pre-filled booking forms to upcoming timeslots.
        
        Returns:
            Upcoming timeslots with forms where necessary.
        """
        for date, timeslots_list in upcoming_timeslots.items():
            for timeslot_info in timeslots_list:
                if not timeslot_info['is_booked']:
                    booking_form = BookKilnForm({
                        'book_timeslot': timeslot_info['timeslot'].id,
                        'day': date.strftime("%Y-%m-%d")
                    })
                    timeslot_info['booking_form'] = booking_form

        return upcoming_timeslots
