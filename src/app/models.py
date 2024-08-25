"""
Custom models in relations to User creation.
User model is managed by allauth.
"""

# from django.db import models

# class Lead(models.Model):
#     """
#     Description:
#         This model represents a lead captured through a web form or other means.
#         It stores the lead's email address and a timestamp of when the lead was created.
#     """

#     email = models.EmailField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         """
#         Description:
#             Returns a string representation of the lead, which is the lead's email address.
#         """
#         return f'{self.email}'
