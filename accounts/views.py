from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from django.urls import reverse


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
