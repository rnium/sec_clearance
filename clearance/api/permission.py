from rest_framework.permissions import BasePermission


class IsSecAcademic(BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'adminaccount') and request.user.adminaccount.user_type == 'academic':
            return True
        return False