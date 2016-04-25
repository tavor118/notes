from rest_framework import permissions


class IsOwnerOrDelegated(permissions.BasePermission):
    """
    Custom permission to only allow owners or delegated user to edit a note.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user


# class AttachEditPermissions

DELEGATED_METHODS_EXCLUDE = ['DELETE']


class CustomNotesPermissions(permissions.BasePermission):
    """
    Custom permissions for access to a note
    """

    def has_object_permission(self, request, view, obj):
        # if current user has permission but he is not owner of the note he can't remove it
        if request.user == obj.owner:
            return True
        if request.user in obj.delegated.all() and request.method not in DELEGATED_METHODS_EXCLUDE:
            return True
        return False


class OwnerPermissions(permissions.BasePermission):
    """
    Custom permissions for access to a note
    """

    def has_object_permission(self, request, view, obj):
        # if current user has permission but he is not owner of the note he can't remove it
        if request.user == obj.owner:
            return True
        return False
