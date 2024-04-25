from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.utils import get_userinfo_data
from accounts.mail_utils import send_clearance_confirmation_email
from accounts.models import StudentAccount, AdminAccount
from accounts.serializer import StudentProfileSerializer
from clearance.models import Department, Lab, Session, Clearance
from clearance.api.utils import (create_clearance_entities, get_administrative_clearance_requests, 
                                 get_dept_head_clearance_requests, get_dept_clerk_clearance_requests, 
                                 get_lab_incharge_clearance_requests, get_dept_sections)
from clearance.api import utils
from clearance.apps import get_model_by_name
from clearance.api.serializer import (AdministrativeApprovalSerializer, DeptApprovalSerializer, ClearanceBasicSerializer,
                                      DeptApprovalBasicSerializer, ClerkApprovalSerializer, LabApprovalSerializer,
                                      DepartmentSeializer)
from clearance.api.pagination import ClearancePagination
from clearance.api.permission import IsAdmin, IsSecAcademic, IsSecAdministrative, IsStudent
from clearance.utils import get_admin_ac, get_student_ac
from django.shortcuts import get_object_or_404
from django.utils import timezone

serializer_mapping = {
    'administrative': AdministrativeApprovalSerializer,
    'dept_head': DeptApprovalSerializer,
    'dept_clerk': ClerkApprovalSerializer,
    'lab_incharge': LabApprovalSerializer,
}

modelname_mapping = {
    'administrative': 'administrativeapproval',
    'dept_head': 'deptapproval',
    'dept_clerk': 'clerkapproval',
    'lab_incharge': 'labapproval',
}

section_getter_mapping = {
    'administrative': get_administrative_clearance_requests,
    'dept_head': get_dept_head_clearance_requests,
    'dept_clerk': get_dept_clerk_clearance_requests,
    'lab_incharge': get_lab_incharge_clearance_requests,
}

class DeparmentList(ListAPIView):
    queryset = Department.objects.all().order_by('id')
    serializer_class = DepartmentSeializer

@api_view()
def get_userinfo(request):
    data = get_userinfo_data(request.user)
    return Response(data=data)


@api_view()
@permission_classes([IsStudent])
def apply_for_clearance(request):
    student = get_student_ac(request)
    if not student.is_approved:
        return Response(data={'details': 'Account not approved'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if hasattr(student, 'clearance'):
        return Response(data={'details': 'Already applied for clearance'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    create_clearance_entities(student)
    return Response(data={'info': 'Applied for clearance'})


@api_view()
@permission_classes([IsAdmin])
def dashboard_clearance_requests(request):
    admin_ac = get_admin_ac(request)
    dept = request.GET.get('dept')
    sections = []
    sections.extend(get_administrative_clearance_requests(admin_ac, 5, dept=dept))
    sections.extend(get_dept_head_clearance_requests(admin_ac, 5, dept=dept))
    sections.extend(get_dept_clerk_clearance_requests(admin_ac, 5, dept=dept))
    sections.extend(get_lab_incharge_clearance_requests(admin_ac, 5, dept=dept))
    return Response(data=sections)


@api_view()
@permission_classes([IsAdmin])
def approve_clearance_entity(request, modelname, pk):
    admin_ac = get_admin_ac(request)
    the_model = get_model_by_name(modelname)
    if the_model is None:
        return Response({'details': 'Unknown action'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    clearance_req = get_object_or_404(the_model, pk=pk)
    if clearance_req.is_approved:
        return Response({'info': 'clearance already approved'}, status=status.HTTP_400_BAD_REQUEST)
    clearance_req.is_approved = True
    clearance_req.approved_by = admin_ac
    clearance_req.approved_at = timezone.now()
    clearance_req.save()
    if clearance_req.clearance.progress == 100:
        send_clearance_confirmation_email(clearance_req.clearance.student)
    return Response({'info': 'Clearance Request Approved'})

@api_view()
@permission_classes([IsAdmin])
def archive_clearance_entity(request, modelname, pk):
    the_model = get_model_by_name(modelname)
    if the_model is None:
        return Response({'details': 'Unknown action'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    clearance_req = get_object_or_404(the_model, pk=pk)
    if clearance_req.is_archived:
        return Response({'details': 'clearance already archived'}, status=status.HTTP_400_BAD_REQUEST)
    clearance_req.is_archived = True
    clearance_req.save()
    return Response({'info': 'Clearance Request Archived'})

@api_view()
@permission_classes([IsAdmin])
def unarchive_clearance_entity(request, modelname, pk):
    the_model = get_model_by_name(modelname)
    if the_model is None:
        return Response({'details': 'Unknown action'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    clearance_req = get_object_or_404(the_model, pk=pk)
    if not clearance_req.is_archived:
        return Response({'details': 'clearance is not archived'}, status=status.HTTP_400_BAD_REQUEST)
    clearance_req.is_archived = False
    clearance_req.save()
    return Response({'info': 'Clearance Request Unarchived'})


@api_view()
@permission_classes([IsAdmin])
def section_clearance(request):
    admin_ac = get_admin_ac(request)
    role_type = request.GET.get('type')
    dept = request.GET.get('dept')
    approved = request.GET.get('approved', 'false') == 'true'
    archived = request.GET.get('archived', 'false') == 'true'
    code = request.GET.get('code', None)
    try:
        Serializer_class = serializer_mapping[role_type]        
        section_getter = section_getter_mapping[role_type]
    except Exception as e:
        print(e)
        return Response({'details': 'Unknown query'}, status=status.HTTP_400_BAD_REQUEST)
    paginator = ClearancePagination()
    sections = section_getter(admin_ac, limit=None, approved=approved, archived=archived, code=code, serialized=False, dept=dept)
    clearance_objects = []
    # print(type(sections[0]['approvals']))
    if len(sections):
        clearance_objects = sections[0]['approvals']
    paginated_queryset = paginator.paginate_queryset(clearance_objects, request)

    serializer = Serializer_class(paginated_queryset, many=True)
    response = paginator.get_paginated_response(serializer.data)
    return response


@api_view()
@permission_classes([IsAdmin])
def dept_sections(request):
    return Response(get_dept_sections())


@api_view(['POST'])
@permission_classes([IsSecAcademic])
def assign_member(request):
    admin_ac = get_admin_ac(request)
    try:
        role = request.data['role']
        code = request.data['code']
        user_id = request.data['user_id']
    except Exception as e:
        return Response({'details': 'Data missing'}, status=status.HTTP_400_BAD_REQUEST)
    target_user = get_object_or_404(AdminAccount, pk=user_id)
    
    if role == 'administrative':
        if admin_ac == target_user:
            return Response({'details': 'Unable to perform this action'}, status=status.HTTP_400_BAD_REQUEST)
        admins_qs = AdminAccount.objects.filter(user_type=code)
        admins_qs.update(user_type='general')
        target_user.user_type = code
        target_user.save()
    elif role in ['dept_head', 'dept_clerk']:
        dept = get_object_or_404(Department, codename=code)
        if role == 'dept_head':
            dept.head = target_user
        elif role == 'dept_clerk' and dept.dept_type in ['administrative', 'hall']:
            dept.clerk = target_user
        dept.save()
    elif role == 'lab_incharge':
        lab = get_object_or_404(Lab, codename=code)
        lab.incharge = target_user
        lab.save()
    else:
        return Response({'details': 'No action to perform'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'info': 'Member Assigned'})


@api_view(['POST'])
@permission_classes([IsSecAcademic])
def unassign_member(request):
    try:
        role = request.data['role']
        code = request.data['code']
        user_id = request.data['user_id']
    except Exception as e:
        return Response({'details': 'Data missing'}, status=status.HTTP_400_BAD_REQUEST)
    target_user = get_object_or_404(AdminAccount, pk=user_id)
    try:
        utils.unassign_member(target_user, role, code)
    except Exception as e:
        return Response({'details': f"Error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'info': 'Member Removed'})


@api_view()
@permission_classes([IsAdmin])
def dept_sessions(request):
    return Response(utils.get_dept_sessions())

@api_view()
@permission_classes([IsAdmin])
def session_students(request):
    session_id = request.GET.get('sessionid')
    session = get_object_or_404(Session, pk=session_id)
    students_qs = session.studentaccount_set.all()
    serializer = StudentProfileSerializer(students_qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsSecAdministrative])
def add_session(request):
    try:
        utils.create_session(request.data)
    except Exception as e:
        return Response({'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'info': 'Session Created'})


@api_view(['GET', 'POST'])
@permission_classes([IsAdmin])
def remarks(request):
    if request.method == 'GET':
        query_dict = request.GET
    elif request.method == 'POST':
        query_dict = request.data
    try:
        approval_type = query_dict['type']
        approval_id = query_dict['id']
        model = get_model_by_name(modelname_mapping[approval_type])
        data = utils.post_or_get_remarks_data(
            model, 
            approval_id,
            approval_type,
            query_dict.get('remarks_text')
        )
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAdmin])
def delete_remarks(request):
    query_dict = request.data
    try:
        approval_type = query_dict['type']
        approval_id = query_dict['id']
        model = get_model_by_name(modelname_mapping[approval_type])
        app_req = get_object_or_404(model, pk=approval_id)
        app_req.remarks = None
        app_req.remarks_added_at = None
        app_req.save()
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response({'info': 'Remarks Deleted'})


@api_view()
@permission_classes([IsStudent])
def student_clearanceinfo(request):
    student = get_student_ac(request)
    if hasattr(student, 'clearance'):
        serializer = ClearanceBasicSerializer(student.clearance)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view()
@permission_classes([IsAdmin])
def clearanceinfo_as_admin(request):
    query_dict = request.GET
    if reg:=query_dict.get('registration'):
        clearance = get_object_or_404(Clearance, student__registration=reg)
        serializer = ClearanceBasicSerializer(clearance)
    else:
        try:
            approval_type = query_dict['type']
            approval_id = query_dict['id']
            The_model = get_model_by_name(modelname_mapping[approval_type])
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        approval = get_object_or_404(The_model, pk=approval_id)
        if approval_type == 'administrative':
            serializer = ClearanceBasicSerializer(approval.clearance)
        elif approval_type == 'dept_head':
            serializer = DeptApprovalBasicSerializer(approval)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.data)

@api_view()
@permission_classes([IsStudent])
def student_remarks_info(request):
    student = get_student_ac(request)
    return Response(utils.get_clearance_remarks(getattr(student, 'clearance')))


@api_view()
@permission_classes([IsAdmin])
def admin_dashboard_stats(request):
    admin_ac = get_admin_ac(request)
    return Response(utils.get_admin_dashboard_stats_data(admin_ac))


class HallList(ListAPIView):
    serializer_class = DepartmentSeializer
    def get_queryset(self):
        return Department.objects.filter(dept_type='hall')