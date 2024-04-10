from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.shortcuts import get_object_or_404
from accounts.serializer import (StudentAccountSerializer, 
                                 PendingStudentSerializer, ProgressiveStudentInfoSerializer)
from accounts.models import StudentAccount
from clearance.models import Session, Department
from django.contrib.auth.models import User
from django.db.models import Q
from accounts.utils import compress_image, get_userinfo_data
from accounts.models import AdminAccount


@api_view(['POST'])
def api_login(request):
    user = authenticate(
        username=request.data['email'], password=request.data['password'])
    if user:
        data = get_userinfo_data(user)
        if(data['is_authenticated']):
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
    
@api_view(['POST'])
def student_signup(request):
    email = request.data['email']
    user_queryset = User.objects.filter(Q(email=email) | Q(username=email))
    if len(user_queryset) > 0:
        return Response({'details':'Email already used'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        dept_codename = request.data['department'].strip().lower()
        dept = Department.objects.get(codename=dept_codename)
    except Exception as e:
        return Response({'details':'Department not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        from_year, to_year = list(map(int, request.data['session'].split('-')))
        to_year += 2000
        session = Session.objects.get(from_year=from_year, to_year=to_year, dept=dept)
    except Exception as e:
        return Response({'details':'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        compressed_dp = compress_image(request.data.get('profilePhoto'))
    except Exception as e:
        return Response({'details':f'Cannot process image. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    # login(request, user=user)
    user = User(
        username = email,
        email = email,
        first_name = request.data.get('first_name'),
        last_name = request.data.get('last_name'),
    )
    try:
        user.set_password(request.data.get('password'))
        user.save()
    except Exception as e:
        return Response({'details':f'Cannot create user. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    account_kwargs = {}
    account_kwargs['user'] = user
    account_kwargs['session'] = session
    account_kwargs['registration'] = request.data.get('registration_no')
    account_kwargs['session'] = session
    account_kwargs['ip_address'] = request.META.get('REMOTE_ADDR')
    account_kwargs['profile_picture'] = compressed_dp
    try:
        student_ac = StudentAccount(**account_kwargs)
        student_ac.save()
    except Exception as e:
        user.delete()
        return Response({'details':f'Cannot create account. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(data={'info': get_userinfo_data(user)})


@api_view(['POST'])
def student_profile_update(request):
    student = StudentAccount.objects.get(registration=2018338502)
    email = request.data.get('email')
    if email:
        user_queryset = User.objects.filter(Q(email=email) | Q(username=email)).exclude(email=student.user.email)
        if len(user_queryset) > 0:
            return Response({'details':'Email already used'}, status=status.HTTP_400_BAD_REQUEST)
    display_pic = request.data.get('profilePhoto')
    if display_pic:
        try:
            display_pic = compress_image(display_pic)
        except Exception as e:
            return Response({'details':f'Cannot process image. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    user = student.user
    if email:
        user.username = email
        user.email = email
    if first_name:=request.data.get('first_name'):
        print('fn')
        user.first_name = first_name
    if last_name:=request.data.get('last_name'):
        print('ln')
        user.last_name = last_name
    if password:=request.data.get('password'):
        print('pass')
        user.password = make_password(password)
        update_session_auth_hash(request, user) 
    try:
        user.save()
    except Exception as e:
        return Response({'details':f'Cannot update user info. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)


    student.ip_address = request.META.get('REMOTE_ADDR')
    if display_pic:
        if student.profile_picture is not None:
            student.profile_picture.delete(save=True)
        student.profile_picture = display_pic
    student.save()
    # try:
    #     student.save()
    # except Exception as e:
    #     return Response({'details':f'Cannot update account. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = ProgressiveStudentInfoSerializer(student)
    return Response(data={'info': serializer.data})


@api_view()
def progressive_studentinfo(request):
    student = StudentAccount.objects.get(registration=2018338502)
    serializer = ProgressiveStudentInfoSerializer(student)
    return Response(data={'info': serializer.data})



@api_view()
def admin_roles(request):
    admin_ac = AdminAccount.objects.filter(user__username='rony').first()
    return Response(data={'info': admin_ac.roles_dict})