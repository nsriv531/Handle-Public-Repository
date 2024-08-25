"""
Database models related only to studio_suite, this is everything explicitly
focused on managing a studio and the objects related to a studio.
"""

from django.db import models
from django.contrib.auth.models import User
import uuid

class StudioInfo(models.Model):
    """
    Description:
        This model stores information about studios, including a unique UUID, 
        a linked user account, a unique URL extension, the studio's name, and a bio.

    Collects:
        uuid (server-managed): primary id is set to be a uuid
        linked_account: User model of the Studio Owner (so that it can be transfered)
        url_extension: Unique url extension used a uri parameter
        name: Public studio name
        bio: Studio description/slogan
        new_member_role: Sets the role of new members based on studio preferences

    Note:
        Although odds of duplicate uuids is astronomically low, this function gaurentees that
        a duplicate will never happen.
    """

    NEW_MEMBER_ROLES = [
        ('NA', 'No Acccess Member'),
        ('RM', 'Regular Member')
    ]

    #made an array to represent the choices for timezones
    TIMEZONE_CHOICES = [ 
        ('Z1', 'GMT'),
        ('Z2', 'MST'),
        ('Z3', 'EST'),
        ('Z4', 'CST'),
        ('Z5', 'PST'),
        ('Z6', 'AEST'),
        ('Z7', 'ACST'),
        ('Z8', 'AWST'),
        ('Z9', 'CET'),
        ('Z10', 'EET')
    ]
   
    #made an array to represent the choices for currency
    CURRENCY_CHOICES = [
        ('C1', 'CAD'),
        ('C2', 'USD'),
        ('C3', 'EUR'),
        ('C4', 'JPY'),
        ('C5', 'GBP'),
        ('C6', 'CHF'),
        ('C7', 'CNY'),
        ('C8', 'AUD'),
        ('C9', 'INR'),
        ('C10', 'BRL')
    ]

    uuid = models.UUIDField(primary_key=True, editable=False)
    linked_account = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    url_extension = models.CharField(max_length=100, unique=True, default="")
    name = models.CharField(max_length=50, unique=True)
    bio = models.TextField()
    business_main_address = models.CharField(max_length=100, default="")
    website_link = models.URLField(default="")
    timezone = models.CharField(max_length=3, default="", choices=TIMEZONE_CHOICES)
    currency = models.CharField(max_length=3, default="", choices=CURRENCY_CHOICES)    
    new_member_role = models.CharField(max_length=2, choices=NEW_MEMBER_ROLES)

    def save(self, *args, **kwargs):
        """
        Description:
            Modified save functionality to ensure a unique UUID on record creation.
        """

        # If creating a user, first gaurentee their uuid is unique.
        if not self.uuid:
            self.uuid = self.generate_unique_uuid()

        # Otherwise use the regular record save function.
        super().save(*args, **kwargs)

    def generate_unique_uuid(self):
        """
        Description:
            Generates a unique UUID for the studio.
        """

        # Generate uuid, check if uuid exists, repeat until the uuid doesn't exist.
        while True: # Astronomically low chance of repetition.
            unique_uuid = uuid.uuid4()
            if not StudioInfo.objects.filter(uuid=unique_uuid).exists():
                return unique_uuid

    def __str__(self):
        """
        Description:
            Returns a string representation of the studio, which is its name.
        """

        return self.name



class MemberStudioRelationship(models.Model):
    """
    Description:
        Defines relationships between members and studios.
    
    Collects:
        member (server managed): User object of the relationship
        studio (server managed): StudioInfo object of the relationship
        member_role: 
            - Members access level within the studio
            - Upon member signup this is auto filled to StudioInfo.new_member_role
            - Can be modified
    """

    MEMBER_ROLE_CHOICES = [
        ('NA', 'No Access Member'),
        ('RM', 'Regular Member'),
        ('TECH', 'Technician'),
        ('MANAGER', 'Studio Manager'),
    ]

    member = models.ForeignKey(User, on_delete=models.CASCADE)
    studio = models.ForeignKey(StudioInfo, on_delete=models.CASCADE)
    member_role = models.CharField(max_length=7, choices=MEMBER_ROLE_CHOICES)

    def __str__(self):
        """
        Description:
            Instead of returning an object reference when being displayed, return the
            member username and studio name.
        """
        return f"Member {self.member.username} linked to Studio {self.studio.name}"
    
    def get_member_role(self):
        """
        Description:
            Method for returning just the members role.
        """
        return self.member_role



class KilnRange(models.Model):
    """
    Description:
        Kiln ranges are the tempature settings for kilns 

    Collects:
        studio (server managed): StudioInfo object that owns this kiln range
        range_name: In case they want to name it the same a kiln or some other use-case.
        min_temp: Minimum temperature
        max_temp: Maximum temperature
        TODO
        kiln_costs: studios can set what booking that kiln will cost a user.
    """

    # Temperature options.
    TEMP_CHOICES = [
        ('Cone 022', 'Cone 022'),
        ('Cone 018', 'Cone 018'),
        ('Cone 06', 'Cone 06'),
        ('Cone 04', 'Cone 04'),
        ('Cone 03', 'Cone 03'),
        ('Cone 5', 'Cone 5'),
        ('Cone 4', 'Cone 4'),
        ('Cone 02', 'Cone 02'),
        ('Cone 1', 'Cone 1'),
        ('Cone 10', 'Cone 10'),
    ]

    studio = models.ForeignKey(StudioInfo, on_delete=models.CASCADE)
    range_name = models.CharField(max_length=100)
    min_temp = models.CharField(max_length=100, choices=TEMP_CHOICES)
    max_temp = models.CharField(max_length=100, choices=TEMP_CHOICES)

    def __str__(self):
        """
        Description:
            When objects are referenced, return the ranges name.
        """
        return f"{self.range_name}"



class KilnManagement(models.Model):
    """
    Description:
        Model to store each studios kilns.

    Collects:
        studio (server managed): StudioInfo object of the studio that owns this kiln
        kiln_name:
            - Has a server managed submission process to make this name unique to the studio
              although different studios can have the same kiln names.
        kiln_make: Description of company that makes the kiln
        kiln_model: Description of kiln model type
        kiln_size: Description of the physical size of kilns firing capacity
        kiln_max_temp: Maximum tempurature of the kiln
        kiln_range: Allows studios to associate a predefined tempature range to the kiln
    """


    studio = models.ForeignKey(StudioInfo, on_delete=models.CASCADE)
    kiln_name = models.CharField(max_length=100)
    kiln_make = models.CharField(max_length=100)
    kiln_model = models.CharField(max_length=100)
    kiln_size = models.CharField(max_length=100)
    kiln_max_temp = models.CharField(max_length=100, choices=KilnRange.TEMP_CHOICES)
    kiln_range = models.ForeignKey('KilnRange', on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        """
        Description:
            When referencing a kiln object, return it's name.
        """
        return f"{self.kiln_name}"



class TimeslotManagement(models.Model):
    """
    Description:
        Database model to store booking schedules of studios.

    Collects:
        studio (server managed): StudioInfo object of what studio owns this timeslot
        kiln: KilnManagement object of which Kiln this timeslot relates to
        min_role_required: Minimum role required to book one of these timeslots
        is_recurring:
            - Never: Only start_date and only occurs on start date
            - Temporarily: Has start and end_date and repeats weekly
            - Forever: Has start daten and repreats weekly forever
        recurrence_frequency: how often the timeslot repeats
        recurring_weekdays:
            - If recurring: Which weekly days does this apply to
        start_date:
            - First day this rule applys to
            - If recurring: start_date must be one of the recurring weekdays
        end_date:
            - If recurring temporarily, what day does this end:
            - If recurring: end_date must be one of the recurring weekdays
        load_after_time: Latest time the kiln will be loaded that day
        notes: A field for studios to add additional info about the timeslot.

        TODO:
        recurrence_frequency can be deleted, artificate from when monthly recurrence existed
    """

    RECURRING_CHOICES = [
        (0, 'Never'),
        (1, 'Temporarily'),
        (2, 'Forever'),
    ]

    RECURRENCE_FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
    ]

    DAYS_OF_WEEK_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    roles_exclude_na = [
        (key, value) for key, value in MemberStudioRelationship.MEMBER_ROLE_CHOICES if key != 'NA'
        ] # Exlude no access from lowest selectable required roles.

    studio = models.ForeignKey(StudioInfo, on_delete=models.CASCADE)
    kiln = models.ForeignKey(KilnManagement, on_delete=models.CASCADE)
    min_role_required = models.CharField(max_length=7,choices=roles_exclude_na)
    is_recurring = models.IntegerField(
        choices=RECURRING_CHOICES,
        default=0,
    )
    recurrence_frequency = models.CharField(
        max_length=10,
        choices=RECURRENCE_FREQUENCY_CHOICES,
        null=True,
        blank=True,
    )
    recurring_weekdays = models.ManyToManyField(
        'Weekday',
        blank=True,
    )
    start_date = models.DateField() #For single day timeslots, stores the bookable date.
    end_date = models.DateField(null=True, blank=True)
    load_after_time = models.TimeField()
    notes = models.TextField(max_length=100, null=True, blank=True)



class Weekday(models.Model):
    """
    Description:
        Database model to store the selectable day options for TimeslotManagement.
        This treats weekdays as objects that can be linked to the studio.
        This is also why we have a database table of just weekday names.
    
    Collects:
        day (admin panel managed on setup):  

    TODO:
    Currently when the application relaunches, these need to be manually associated
    with the table through the admin panel. I want the app to be able to check
    if these exists whenever it starts and if they dont, then automatically fill the
    table.
    """

    day = models.CharField(
        max_length=10,
        choices=TimeslotManagement.DAYS_OF_WEEK_CHOICES,
        unique=True,
    )

    def __str__(self):
        """
        Description:
            When a day object is referenced, return the weekday display name.   
        """
        return self.get_day_display()



class TimeslotBlackout(models.Model):
    """
    Description:
        Store the time intervals for blackouts of timeslots, can be completed manually or as a
        automatic collision warning remediation.

    Collects:
        studio (server managed): unused
        related_timeslot: unused
        blackout_start_datetime: unused
        blackout_end_datetime: unused
        blackout_reason: unused
    
    TODO:
    We havent decided what the blackout system looks like, this is currently completely unused
    all related forms and code that could allow a user to interact with this model should be
    commented out (and therefor unusable).
    """

    studio = models.ForeignKey(StudioInfo, on_delete=models.CASCADE)
    related_timeslot = models.ForeignKey(TimeslotManagement, on_delete=models.CASCADE)
    blackout_start_datetime = models.DateTimeField()
    blackout_end_datetime = models.DateTimeField()
    blackout_reason = models.TextField(max_length=100, null=True, blank=True)
