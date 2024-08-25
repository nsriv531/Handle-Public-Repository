"""
Database models related only to MEMBERS, will be updated
if members have their own table unrelated to studios.

"""

from django.db import models
from studio_suite.models import StudioInfo, TimeslotManagement
from django.contrib.auth.models import User

class BookingManagement(models.Model):
    """
    Description:
        Database model to store booking schedules of studios.
    
    Collects:
        studio: StudioInfo object
        member: User object
        timeslot: TimeslotManagement object
        booking_date: Day of the requested booking 

    Security:
        TODO
        Verify member is related to studio
        Verify member has the correct permissions for the timeslot
    """

    studio = models.ForeignKey(StudioInfo, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeslotManagement, on_delete=models.CASCADE)
    booking_date = models.DateTimeField()