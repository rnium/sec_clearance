from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.utils import get_userinfo_data
from accounts.models import StudentAccount
from clearance.api.utils import create_clearance_entities

@api_view()
def get_userinfo(request):
    data = get_userinfo_data(request.user)
    return Response(data=data)


@api_view()
def apply_for_clearance(request):
    student = StudentAccount.objects.get(registration=2018338514)
    if not student.is_approved:
        return Response(data={'details': 'Account not approved'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if hasattr(student, 'clearance'):
        return Response(data={'details': 'Already applied for clearance'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    create_clearance_entities(student)
    return Response(data={'info': 'Applied for clearance'})