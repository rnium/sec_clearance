from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.shortcuts import get_object_or_404
from accounts.serializer import (StudentAccountSerializer, AdminAccountBasicSerializer, 
                                 PendingStudentSerializer, ProgressiveStudentInfoSerializer)
from accounts.models import StudentAccount
from clearance.models import Session, Department
from django.contrib.auth.models import User
from django.db.models import Q
from clearance.utils import get_admin_roles
from accounts.utils import compress_image, get_userinfo_data, get_members_data
from accounts import utils
from accounts.mail_utils import send_signup_email, send_html_email, send_student_ac_confirmation_email
from accounts.models import AdminAccount, InviteToken
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q
from datetime import timedelta


@api_view()
def validate_token(request):
    tokenid = request.GET.get('tokenid')
    token = InviteToken.objects.filter(pk=tokenid).first()
    if not token or not token.is_valid():
        return Response({'details':'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'info':'Valid Token'})
 
@api_view(['POST'])
def admin_signup(request):
    tokenid = request.data.get('tokenid')
    token = InviteToken.objects.filter(pk=tokenid).first()
    if not token or not token.is_valid():
        return Response({'details':'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
    email = token.user_email
    user_queryset = User.objects.filter(Q(email=email) | Q(username=email))
    if len(user_queryset) > 0:
        return Response({'details':'Email already used'}, status=status.HTTP_400_BAD_REQUEST)
    photo = request.data.get('profilePhoto')
    compressed_dp = None
    if photo:
        try:
            compressed_dp = compress_image(photo)
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
    account_kwargs['dept'] = Department.objects.filter(id=token.to_user_dept_id).first()
    account_kwargs['invited_by'] = token.from_user
    account_kwargs['profile_picture'] = compressed_dp
    try:
        admin_ac = AdminAccount(**account_kwargs)
        admin_ac.save()
    except Exception as e:
        user.delete()
        return Response({'details':f'Cannot create account. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    token.delete()
    return Response(data={'info': 'Account Created Successfully'})



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


@api_view(['POST'])
def api_logout(request):
    logout(request)
    return Response({'info': 'Logged Out'})

class PendingStudents(ListAPIView):
    serializer_class = PendingStudentSerializer
    def get_queryset(self):
        dept = self.request.GET.get('dept')
        return StudentAccount.objects.filter(is_approved=False, session__dept__codename=dept).order_by('user__date_joined')
    
    


@api_view(['POST'])
def admin_profile_update(request):
    admin_ac = request.user.adminaccount
    email = request.data.get('email')
    if email:
        user_queryset = User.objects.filter(Q(email=email) | Q(username=email)).exclude(email=admin_ac.user.email)
        if len(user_queryset) > 0:
            return Response({'details':'Email already used'}, status=status.HTTP_400_BAD_REQUEST)
    display_pic = request.data.get('profilePhoto')
    if display_pic:
        try:
            display_pic = compress_image(display_pic)
        except Exception as e:
            return Response({'details':f'Cannot process image. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    user = admin_ac.user
    if email:
        user.username = email
        user.email = email
    if first_name:=request.data.get('first_name'):
        if (len(first_name)):
            user.first_name = first_name
    if last_name:=request.data.get('last_name'):
        if (len(last_name)):
            user.last_name = last_name
    if password:=request.data.get('password'):
        user.password = make_password(password)
        update_session_auth_hash(request, user) 
    try:
        user.save()
    except Exception as e:
        return Response({'details':f'Cannot update user info. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)

    if display_pic:
        if admin_ac.profile_picture is not None:
            admin_ac.profile_picture.delete(save=True)
        admin_ac.profile_picture = display_pic
    admin_ac.save()
    # try:
    #     student.save()
    # except Exception as e:
    #     return Response({'details':f'Cannot update account. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    data = utils.get_userinfo_data(user)
    return Response(data)



@api_view(['POST'])
def approve_student_ac(request):
    try:
        reg = request.data['registration']
    except KeyError:
        return Response(data={'details': 'Registration empty'}, status=status.HTTP_400_BAD_REQUEST)
    student_ac = get_object_or_404(StudentAccount, pk=reg)
    if student_ac.is_approved:
        return Response(data={'details': 'Account already approved'}, status=status.HTTP_400_BAD_REQUEST)
    if not send_student_ac_confirmation_email(student_ac):
        return Response(data={'details': 'Cannot send verification mail, aborted'}, status=status.HTTP_400_BAD_REQUEST)
    student_ac.is_approved = True
    student_ac.save()
    return Response(data={'info': 'Account Approved'})


@api_view(['POST'])
def approve_all_student_ac(request):
    dept = request.data.get('dept')
    if dept is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    student_acs = StudentAccount.objects.filter(is_approved=False, session__dept__codename=dept)
    count = 0
    for ac in student_acs:
        if send_student_ac_confirmation_email(ac):
            ac.is_approved = True
            ac.save()
            count += 1
    return Response(data={'info': f'{count} Student Account Approved'})


@api_view(['POST'])
def delete_student_ac(request):
    try:
        reg = request.data['registration']
    except KeyError:
        return Response(data={'details': 'Registration empty'}, status=status.HTTP_400_BAD_REQUEST)
    student_ac = get_object_or_404(StudentAccount, pk=reg)
    if hasattr(student_ac, 'clearance'):
        return Response(data={'details': 'Cannot Delete Now, Student applied for clearance'}, status=status.HTTP_400_BAD_REQUEST)
    student_ac.delete()
    return Response(data={'info': 'Account Deleted'})

 
@api_view(['POST'])
def student_signup(request):
    email = request.data['email']
    user_queryset = User.objects.filter(Q(email=email) | Q(username=email))
    student_ac_qs = StudentAccount.objects.filter(registration=request.data.get('registration_no'))
    if user_queryset.count():
        return Response({'details':'Email already used'}, status=status.HTTP_400_BAD_REQUEST)
    if student_ac_qs.count():
        return Response({'details':'Student Already Signed Up'}, status=status.HTTP_400_BAD_REQUEST)
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
    account_kwargs['phone'] = request.data.get('phone')
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
    student = request.user.studentaccount
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
    student = request.user.studentaccount
    serializer = ProgressiveStudentInfoSerializer(student)
    return Response(data={'info': serializer.data})



@api_view()
def admin_roles(request):
    # admin_ac = request.user.adminaccount
    admin_ac = AdminAccount.objects.get(user__username='rony')
    return Response(data={'info': get_admin_roles(admin_ac)})


@api_view()
def members(request):
    data = get_members_data()
    return Response(data)


@api_view(['POST'])
def send_invitation(request):
    from_user = request.user
    try:
        to_user_email = request.data['email']
        dept_id = request.data['dept']
    except KeyError:
        return Response(data={'details': "Data Missing"}, status=status.HTTP_400_BAD_REQUEST)
    if dept_id == -1:
        dept_id = None
    # checking if user exists with this email
    users = User.objects.filter(email=to_user_email)
    if users.count():
        return Response(data={'details': "User with this email already exists!"}, status=status.HTTP_400_BAD_REQUEST)
    
    expiration = timezone.now() + timedelta(days=7)
    invite_token = InviteToken(
        from_user = from_user,
        user_email = to_user_email,
        to_user_dept_id = dept_id,
        expiration = expiration,
    )
    invite_token.save()
    success = send_signup_email(request, invite_token)
    if not success:
        invite_token.delete()
        return Response({'details': 'Cannot Send Email'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({'info': 'Invitation Sent'})

@api_view()
def search_member(request):
    query = request.GET.get('query', None)
    if query is None:
        return Response({'details': 'Empty query!'}, status=status.HTTP_400_BAD_REQUEST)
    members = AdminAccount.objects.filter(
        Q(user__first_name__startswith=query) |
        Q(user__last_name__startswith=query) |
        Q(user__email__startswith=query)
    )
    serializer = AdminAccountBasicSerializer(members[:3], many=True)
    return Response(serializer.data)


# Account Recovery API's
@api_view(["POST"])
def send_recovery_email(request):
    email_subject = "Password Recovery"
    try:
        email = request.data['email']
    except Exception as e:
        return Response(data={"error":"No email provided"}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.filter(email=email).first()
    if user is None:
        return Response(data={'details':'No user found with this email'}, status=status.HTTP_404_NOT_FOUND)

    uid = urlsafe_base64_encode(force_bytes(user.id))
    token = default_token_generator.make_token(user)
    recovery_url = request.build_absolute_uri(reverse("accounts:reset_password_form", args=(uid, token)))
    email_body = render_to_string('accounts/recovery_mail.html', context={
        "user": user,
        "recovery_url": recovery_url
    })
    try:
        send_html_email(user.email, email_subject, email_body)
    except Exception as e:
        return Response(data={'details':'Cannot Send Email'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(data={"info":"Recovery Email Sent, Please check Inbox/Spam folder"}, status=status.HTTP_200_OK)
    
    
@api_view(["POST"])
def reset_password(request):
    try:
        uidb64 = request.data['uid'] 
        token = request.data['token']
        new_pass = request.data['password']
    except Exception as e:
        return Response(data={"details":"Required data missing"}, status=status.HTTP_400_BAD_REQUEST)
    try :
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except Exception as e:
        return Response(data={"details":"User not found"}, status=status.HTTP_404_NOT_FOUND)
    if not default_token_generator.check_token(user, token):
        return Response(data={"details":"Invalid or expired recovery link"}, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_pass)
    user.save()
    logout(request)
    return Response(data={"info":"Password Reset Successful"},status=status.HTTP_200_OK)