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
from accounts.models import StudentAccount, StudentPlaceholder
from clearance.models import Session, Department
from django.contrib.auth.models import User
from django.db.models import Q
from clearance.utils import get_admin_roles, get_admin_ac, get_student_ac
from accounts.utils import compress_image, get_userinfo_data, get_members_data
from accounts import utils
from accounts.mail_utils import send_signup_email, send_html_email, send_student_ac_confirmation_email
from accounts.models import AdminAccount, InviteToken
from django.utils import timezone
from django.http import HttpResponse
from clearance.api.permission import IsAdmin, IsSecAcademic, IsSecAdministrative, IsSecAdministrativeIncludingCashier, IsStudent
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
    phone = request.data.get('phone', '')
    if not phone.isdigit() or len(phone) != 11:
        return Response({'details':f'Invalid Phone Number'}, status=status.HTTP_400_BAD_REQUEST)
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
    account_kwargs['phone'] = phone
    try:
        admin_ac = AdminAccount(**account_kwargs)
        admin_ac.save()
    except Exception as e:
        user.delete()
        return Response({'details':f'Cannot create account. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    token.delete()
    login(request, user)
    data = get_userinfo_data(user)
    return Response({'data': data})



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
    permission_classes = [IsSecAcademic]
    def get_queryset(self):
        dept = self.request.GET.get('dept')
        return StudentAccount.objects.filter(is_approved=False, session__dept__codename=dept).order_by('user__date_joined')
    
    


@api_view(['POST'])
@permission_classes([IsAdmin])
def admin_profile_update(request):
    admin_ac = get_admin_ac(request)
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
    if phone:=request.data.get('phone'):
        if not phone.isdigit() or len(phone) != 11:
            return Response({'details':f'Invalid Phone Number'}, status=status.HTTP_400_BAD_REQUEST)
        admin_ac.phone = phone
    if display_pic:
        if admin_ac.profile_picture is not None:
            admin_ac.profile_picture.delete(save=True)
        admin_ac.profile_picture = display_pic
    try:
        admin_ac.save()
    except Exception as e:
        return Response({'details':f'Cannot update account. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    data = utils.get_userinfo_data(user)
    return Response(data)



@api_view(['POST'])
@permission_classes([IsSecAcademic])
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
@permission_classes([IsSecAcademic])
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
@permission_classes([IsSecAdministrative])
def delete_student_ac(request):
    try:
        reg = request.data['registration']
    except KeyError:
        return Response(data={'details': 'Registration empty'}, status=status.HTTP_400_BAD_REQUEST)
    student_ac = get_object_or_404(StudentAccount, pk=reg)
    if hasattr(student_ac, 'clearance') and student_ac.clearance.progress == 100:
        return Response(data={'details': 'Cannot Delete Now, Student received 100% clearance'}, status=status.HTTP_400_BAD_REQUEST)
    StudentPlaceholder.objects.get_or_create(registration=student_ac.registration, session=student_ac.session)
    student_ac.user.delete()
    return Response(data={'info': 'Account Deleted'})

 
@api_view(['POST'])
def student_signup(request):
    email = request.data['email']
    reg_no = request.data.get('registration_no')
    user_queryset = User.objects.filter(Q(email=email) | Q(username=email))
    student_ac_qs = StudentAccount.objects.filter(registration=reg_no)
    if user_queryset.count():
        return Response({'details':'Email already used'}, status=status.HTTP_400_BAD_REQUEST)
    if student_ac_qs.count():
        return Response({'details':'Student With This Registration Already Signed Up'}, status=status.HTTP_400_BAD_REQUEST)
    placeholder = StudentPlaceholder.objects.filter(registration=reg_no).first()
    academic = AdminAccount.objects.filter(user_type='academic').first()
    academic_mail = ':('
    if academic:
        academic_mail = academic.user.email
    if placeholder is None:
        return Response({'details':f'Your registration is not in the system. Email `{academic_mail}` to add you'}, status=status.HTTP_404_NOT_FOUND)
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
    hall = Department.objects.filter(dept_type='hall', pk=request.data.get('hall')).first()
    account_kwargs = {}
    account_kwargs['user'] = user
    account_kwargs['session'] = placeholder.session
    account_kwargs['registration'] = reg_no
    account_kwargs['hall'] = hall
    account_kwargs['phone'] = request.data.get('phone')
    account_kwargs['profile_picture'] = compressed_dp
    try:
        student_ac = StudentAccount(**account_kwargs)
        student_ac.save()
    except Exception as e:
        user.delete()
        return Response({'details':f'Cannot create account. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    login(request, user)
    placeholder.delete()
    return Response(data={'info': get_userinfo_data(user)})


@api_view(['POST'])
@permission_classes([IsStudent])
def student_profile_update(request):
    student = get_student_ac(request)
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
    hall_id = request.data.get('hall')
    if hall_id is not None:
        if hasattr(student, 'clearance'):
            return Response({'details':'You Cannot Change Hall Now! Please contact administrators to change hall.'}, status=status.HTTP_400_BAD_REQUEST)
        student.hall = Department.objects.filter(dept_type='hall', pk=hall_id).first()
    if display_pic:
        if student.profile_picture is not None:
            student.profile_picture.delete(save=True)
        student.profile_picture = display_pic
    try:
        student.save()
    except Exception as e:
        return Response({'details':f'Cannot update account. Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = ProgressiveStudentInfoSerializer(student)
    return Response(data={'info': serializer.data})


@api_view(['POST'])
@permission_classes([IsSecAdministrativeIncludingCashier])
def student_profile_update_by_admin(request):
    try:
        utils.update_student_profile_as_admin(request.data)
    except Exception as e:
        return Response({'details': f'Cannot Update Data, error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'info': 'Updated'})

@api_view()
@permission_classes([IsStudent])
def progressive_studentinfo(request):
    student = get_student_ac(request)
    serializer = ProgressiveStudentInfoSerializer(student)
    return Response(data={'info': serializer.data})



@api_view()
@permission_classes([IsAdmin])
def admin_roles(request):
    admin_ac = get_admin_ac(request)
    return Response(data={'info': get_admin_roles(admin_ac)})


@api_view()
@permission_classes([IsAdmin])
def members(request):
    data = get_members_data()
    return Response(data)


@api_view(['POST'])
@permission_classes([IsSecAdministrative])
def send_invitation(request):
    from_user = get_admin_ac(request).user
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


@api_view(['POST'])
@permission_classes([IsSecAdministrative])
def change_dept(request):
    admin_ac = get_object_or_404(AdminAccount, pk=request.data.get('user_id'))
    dept_pk = request.data.get('dept')
    if dept_pk and dept_pk >= 0:
        dept = get_object_or_404(Department, pk=dept_pk)
    else:
        dept = None
    admin_ac.dept = dept
    admin_ac.save()
    return Response({'info': f'Department Changed for {admin_ac.full_name}'})


@api_view(['POST'])
@permission_classes([IsSecAdministrative])
def delete_account(request):
    admin_ac = get_object_or_404(AdminAccount, pk=request.data.get('user_id'))
    if admin_ac == request.user.adminaccount:
        return Response({'details': 'You cannot delete your own account'}, status=status.HTTP_400_BAD_REQUEST)
    name = admin_ac.full_name
    admin_ac.user.delete()
    return Response({'info': f'Account of {name} has been deleted'})



@api_view(['POST'])
@permission_classes([IsSecAdministrative])
def process_reg_excel(request):
    success, info = utils.process_reg_placeholder_excel(request)
    if not success:
        return Response(data={'details': info}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'info': info})


@api_view()
@permission_classes([IsSecAdministrative])
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