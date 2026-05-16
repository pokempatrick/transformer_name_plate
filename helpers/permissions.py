from datetime import date, datetime
import os
from django.utils import timezone
from rest_framework import permissions
from helpers import constant
from helpers.utils import hour_diff


class IsAuthenficatedOnly(permissions.BasePermission):
    message = "Only authenticated can perform this action"

    def has_permission(self, request, view):
        """
            Return `True` if permission is granted, `False` otherwise.
        """
        return bool(request.user and request.user.is_authenticated)


class IsGrantedAccess(permissions.BasePermission):
    message = "Your access to this application is canceled"

    def has_permission(self, request, view):
        """
            Return `True` if permission is granted, `False` otherwise.
        """
        return bool((request.user.role_name in constant.ROLE_ADMIN_HERITED)
                    or (request.user.limited_access_date > date.today()))


class HasAdminRole(permissions.BasePermission):
    message = "Only admin can perform this action"

    def has_permission(self, request, view):
        """
            Return `True` if permission is granted, `False` otherwise.
        """
        if (request.method in permissions.SAFE_METHODS):
            return True

        return request.user.role_name in constant.ROLE_ADMIN_HERITED


class HasOWNERRole(permissions.BasePermission):
    message = "Only owner can perform this action"

    def has_object_permission(self, request, view, obj):
        """
            Return `True` if permission is granted, `False` otherwise.
        """
        if (request.method in permissions.SAFE_METHODS):
            return True
        return request.user.role_name in constant.ROLE_OWNER_HERITED


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = "Only owner can perform this action"

    def has_permission(self, request, view):
        """
            Return `True` if permission is granted, `False` otherwise.
        """
        if (request.method in permissions.SAFE_METHODS):
            return True
        return request.user.role_name in constant.ROLE_OWNER_HERITED


class IsTeamMember(permissions.BasePermission):
    message = "Only team members can perform this action"

    def has_permission(self, request, view):
        """
            Return `True` if permission is granted, `False` otherwise.
        """
        if (request.method in permissions.SAFE_METHODS):
            return True
        return request.user.role_name in constant.ROLE_MANAGER


class IsUserOwner(permissions.BasePermission):
    message = "Only the owner can perform this action"

    def has_object_permission(self, request, view, obj):
        """
            Return `True` if permission is granted, `False` otherwise.
        """
        if (request.method in permissions.SAFE_METHODS):
            return True
        return request.user == obj


class IsNew(permissions.BasePermission):
    message = "You can't change it after " + \
        f'{os.environ.get('DELAY_TIME')}' + "hour."

    def has_object_permission(self, request, view, obj):
        """
            Return `True` if permission is granted, `False` otherwise.
        """
        if (request.method in permissions.SAFE_METHODS):
            return True
        return hour_diff(obj.created_at, timezone.now()) < int(os.environ.get('DELAY_TIME'))
