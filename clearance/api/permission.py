from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'adminaccount'):
            return True
        return False


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'studentaccount'):
            return True
        return False


class IsSecAcademic(BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'adminaccount') and request.user.adminaccount.user_type == 'academic':
            return True
        return False


class IsSecAdministrative(BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'adminaccount') and request.user.adminaccount.user_type in ['principal', 'academic']:
            return True
        return False


class IsSecAdministrativeIncludingCashier(BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'adminaccount') and request.user.adminaccount.user_type in ['principal', 'academic', 'cashier']:
            return True
        return False
    
class IsAcademicOrNonAcademicReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return hasattr(request.user, 'adminaccount') and request.user.adminaccount.user_type == 'academic'