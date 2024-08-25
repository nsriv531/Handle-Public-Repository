"""
This module will contain Django admin configurations for managing member_suite specific
models and their data through the Django admin interface. 
"""

from django.contrib import admin
from .models import (
    StudioInfo,
    MemberStudioRelationship,
    KilnRange,
    KilnManagement,
    TimeslotManagement,
    Weekday,
    # TimeslotBlackout
)


class StudioInfoAdmin(admin.ModelAdmin):
    """
    Description:
        Defines the admin configuration for the 'StudioInfo' model.
    """

    list_display = ('name', 'linked_account', 'url_extension', 'business_main_address', 'website_link', 'timezone', 'currency', 'uuid', 'new_member_role')
    list_display_links = ('name', 'linked_account', 'url_extension', 'new_member_role')
    search_fields = ('name', 'linked_account__username', 'uuid', 'linked_account__email', 'business_main_address')
    list_filter = ('linked_account',)
    list_per_page = 25



class MemberStudioRelationshipAdmin(admin.ModelAdmin):
    """
    Description:
        Defines the admin configuration for the 'MemberStudioRelationship' model.
    """

    list_display = ('member', 'studio', 'member_role')
    list_display_links = ('member', 'studio', 'member_role')

    def studio_link(self, obj):
        """ A custom method to display the studio name as 'Studio'. """
        return obj.studio.name

    studio_link.short_description = 'Studio'



class KilnRangeAdmin(admin.ModelAdmin):
    """
    Description:
        Defines the admin configurations for the Kiln (Temperature) Range Objects
    """
    list_display = ['range_name', 'studio', 'min_temp', 'max_temp']
    list_filter = ['studio']



class KilnManagementAdmin(admin.ModelAdmin):
    """
    Description:
        Defines the admin configurations for the Kiln Objects
    """

    list_display = ('studio', 'kiln_name', 'kiln_make', 'kiln_model', 'kiln_size', 'kiln_max_temp')
    list_filter = ('studio', 'kiln_make', 'kiln_model')
    search_fields = ('studio', 'kiln_name', 'kiln_make', 'kiln_model', 'kiln_size', 'kiln_max_temp')

    def display_kiln_max_temp(self, obj):
        """
        Description:
            Define a custom method for displaying the dropdown menu
        """

        return dict(KilnManagement.KILN_MAX_TEMP_CHOICES).get(obj.kiln_max_temp, obj.kiln_max_temp)



class TimeslotManagementAdmin(admin.ModelAdmin):
    """
    Description:
        Defines the admin configuration for the 'TimeslotManagement' model.
    """

    list_display = (
        'studio', 'kiln', 'is_recurring', 'start_date', 'end_date',
        'recurrence_frequency', 'load_after_time', 'get_recurring_weekdays',
        )
    list_filter = ('is_recurring', 'recurrence_frequency')
    search_fields = ('studio__name', 'kiln__name', 'notes')
    list_per_page = 20
    filter_horizontal = ('recurring_weekdays',)

    def get_recurring_weekdays(self, obj):
        """
        Description:
            This function takes an object that has a many-to-many relationship with recurring weekdays
            and returns a readable list of those weekdays, separated by commas.
        """

        return ", ".join([day.get_day_display() for day in obj.recurring_weekdays.all()])
    get_recurring_weekdays.short_description = 'Recurring Weekdays'



admin.site.register(StudioInfo, StudioInfoAdmin)
admin.site.register(MemberStudioRelationship, MemberStudioRelationshipAdmin)
admin.site.register(KilnManagement, KilnManagementAdmin)
admin.site.register(Weekday)
admin.site.register(TimeslotManagement, TimeslotManagementAdmin)
admin.site.register(KilnRange, KilnRangeAdmin)