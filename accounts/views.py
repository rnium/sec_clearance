from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, DestroyAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.shortcuts import get_object_or_404
from accounts.serializer import StudentAccountSerializer, PendingStudentSerializer
from accounts.models import StudentAccount


@api_view(['POST'])
def api_login(request):
    user = authenticate(
        username=request.data['email'], password=request.data['password'])
    if user:
        data = {
            'is_authenticated': False,
            'username': '',
            'user_fullname': '',
            'account_type': '',
            'user_type': '',
        }
        if hasattr(user, 'adminaccount'):
            admin_ac = user.adminaccount
            data['account_type'] = 'admin'
            data['username'] = user.get_username()
            data['user_type'] = admin_ac.user_type
            data['user_fullname'] = admin_ac.full_name
        elif hasattr(user, 'studentaccount'):
            student_ac = user.studentaccount
            data['account_type'] = 'student'
            data['username'] = user.get_username()
            data['user_fullname'] = student_ac.full_name
        else:
            return Response(data={'details': 'User has no associated account!'}, status=status.HTTP_400_BAD_REQUEST)
        data['is_authenticated'] = True
        login(request, user)
        return Response({'data': data})
    else:
        return Response({'details': 'Invalid Credentials'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class PendingStudents(ListAPIView):
    serializer_class = PendingStudentSerializer
    queryset = StudentAccount.objects.filter(is_approved=False).order_by('user__date_joined')


@api_view(['POST'])
def approve_student_ac(request, registration):
    student_ac = get_object_or_404(StudentAccount, pk=registration)
    student_ac.is_approved = True
    student_ac.save()
    return Response(data={'info': 'Account Approved'})


class DeleteStudentAc(DestroyAPIView):
    queryset = StudentAccount.objects.filter(is_approved=False).order_by('user__date_joined')
    serializer_class = StudentAccountSerializer