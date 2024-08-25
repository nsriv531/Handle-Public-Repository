"""
Decorators related to basic route authorization and route protection.
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from studio_suite.models import MemberStudioRelationship, StudioInfo
from django.http import Http404

def member_group_required(func):
    """
    Description:
        Decorator dictating access to routes of studio members.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Description:
            Wraps routes in the member_suite to make sure a user has a studio relationship
            Allows the studio owner to access the routes as well.
        """
        if len(args) > 1 and hasattr(args[1], 'user'):
            self, request = args[:2]
            studio_url_extension = kwargs.get('studio_url_extension')
            studio = get_object_or_404(StudioInfo, url_extension=studio_url_extension)
            user = request.user

            # Check if the user is associated with the specified studio
            if not MemberStudioRelationship.objects.filter(member=user, studio=studio).exists() and studio.linked_account != request.user:
                # Technically raising a 404 is not proper, however, they will only get this 404 if they're attempting
                # 1 of 2 possibly malicious techniques.Therefor, we should pretend as if the page doesn't exists.
                raise Http404()

            return func(*args, **kwargs)

    return wrapper


def studio_ownership_required(func):
    """
    Description:
        Decorator dictating access to routes of studio owners.
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        """
        Description:
            Wraps routes in the studio_suite to make sure tje accessing use is the studio owner.
        """
        studio = get_object_or_404(StudioInfo, url_extension=kwargs.get('studio_url_extension'))

        if studio.linked_account != request.user:
            # Technically raising a 404 is not proper, however, they will only get this 404 if they're attempting
            # 1 of 2 possibly malicious techniques. Therefor, we should pretend as if the page doesn't exists.
            raise Http404()

        return func(self, request, *args, **kwargs)

    return wrapper