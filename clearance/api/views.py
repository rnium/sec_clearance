from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.utils import get_userinfo_data


@api_view()
def get_userinfo(request):
    data = get_userinfo_data(request)
    return Response(data=data)
    
    