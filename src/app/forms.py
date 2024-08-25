"""
Custom forms served in relation to signup authorization.
"""

from django import forms
from django.contrib.auth.models import User
# from .models import Lead
from django.contrib.auth.forms import UserChangeForm


# class LeadForm(forms.ModelForm):
#     """
#     Description:
#         This form is used for creating or updating Lead objects based on the 'Lead' model.
#         It allows users to enter an email address to associate with a lead.
    
#     Collects:
#         User Email.
#     """
#     class Meta:
#         """
#         Description:
#             Configuration class specifying the associated model and fields.
#         """
#         model = Lead
#         fields = ['email']


class RestrictedUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)
