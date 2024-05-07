from rest_framework.permissions import BasePermission


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