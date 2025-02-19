from django.conf import settings
from rest_framework.exceptions import ParseError
from rest_framework.permissions import BasePermission


class IsAPIKeyAuthenticated(BasePermission):
    """
    Custom permission class to authenticate requests using an API key.

    This permission class checks whether the API key provided in the request headers matches the expected API key
    defined in the Django settings.

    Raises:
        ParseError: If the API key is not provided in the request headers or if it does not match the expected API key.

    Attributes:
        message (str): A message that will be included in the response if the permission is denied.
    """

    message = {"error": "Invalid API-KEY."}

    def has_permission(self, request, view):
        """
        Returns:
            bool: True if the API key is valid, False otherwise.
        """
        api_key_secret = request.META.get("HTTP_API_KEY")
        if not api_key_secret:
            raise ParseError({"error": "API-KEY is required."})
        if api_key_secret == settings.API_KEY:
            return True
        return False


class IsRoleAuthorOrAdmin(BasePermission):
    """
    Custom permission to only allow access to Authors or Admins only.
    """

    message = {"error": "Only Authors and Admins are allowed to perform this action."}

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        if request.user.role == "Admin":
            return True
        return request.user.role == "Author"


class IsRoleReaderOrAdmin(BasePermission):
    """
    Custom permission to only allow access to Readers or Admins only.
    """

    message = {"error": "Only Readers and Admins are allowed to perform this action."}

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        if request.user.role == "Admin":
            return True
        return request.user.role == "Reader"


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow access to objects created by the requesting user.
    """

    message = {
        "error": "You do not have permission to perform this action on another user's resource."
    }

    def has_object_permission(self, request, view, obj):
        if request.user.role == "Admin":
            return True
        # Check if the requesting user is the creator of the object
        return obj.user == request.user
