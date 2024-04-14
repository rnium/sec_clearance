from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.utils import get_userinfo_data
from accounts.models import StudentAccount, AdminAccount
from clearance.models import Department, Lab
from clearance.api.utils import (create_clearance_entities, get_administrative_clearance_requests, 
                                 get_dept_head_clearance_requests, get_dept_clerk_clearance_requests, 
                                 get_lab_incharge_clearance_requests, get_dept_sections)
from clearance.apps import get_model_by_name
from clearance.api.serializer import (AdministrativeApprovalSerializer, DeptApprovalSerializer, 
                                      ClerkApprovalSerializer, LabApprovalSerializer, DepartmentSeializer)
from clearance.api.pagination import ClearancePagination
from django.shortcuts import get_object_or_404
from django.utils import timezone

serializer_mapping = {
    'administrative': AdministrativeApprovalSerializer,
    'dept_head': DeptApprovalSerializer,
    'dept_clerk': ClerkApprovalSerializer,
    'lab_incharge': LabApprovalSerializer,
}

model_mapping = {
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
    queryset = Department.objects.all()
    serializer_class = DepartmentSeializer

@api_view()
def get_userinfo(request):
    data = get_userinfo_data(request.user)
    return Response(data=data)


@api_view()
def apply_for_clearance(request):
    student = StudentAccount.objects.get(registration=2018338502)
    if not student.is_approved:
        return Response(data={'details': 'Account not approved'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if hasattr(student, 'clearance'):
        return Response(data={'details': 'Already applied for clearance'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    create_clearance_entities(student)
    return Response(data={'info': 'Applied for clearance'})


@api_view()
def dashboard_clearance_requests(request):
    admin_ac = AdminAccount.objects.filter(user__username='rony').first()
    sections = []
    sections.extend(get_administrative_clearance_requests(admin_ac, 5))
    sections.extend(get_dept_head_clearance_requests(admin_ac, 5))
    sections.extend(get_dept_clerk_clearance_requests(admin_ac, 5))
    sections.extend(get_lab_incharge_clearance_requests(admin_ac, 5))
    return Response(data=sections)


@api_view()
def approve_clearance_entity(request, modelname, pk):
    admin_ac = AdminAccount.objects.filter(user__username='rony').first()
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
    return Response({'info': 'Clearance Request Approved'})

@api_view()
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
def section_clearance(request):
    admin_ac = AdminAccount.objects.filter(user__username='rony').first()
    role_type = request.GET.get('type')
    approved = bool(request.GET.get('approved', False))
    archived = bool(request.GET.get('archived', False))
    code = request.GET.get('code', None)
    try:
        Serializer_class = serializer_mapping[role_type]
        # The_model = get_model_by_name(model_mapping[role_type])
        
        section_getter = section_getter_mapping[role_type]
    except Exception as e:
        print(e)
        return Response({'details': 'Unknown query'}, status=status.HTTP_400_BAD_REQUEST)
    paginator = ClearancePagination()
    sections = section_getter(admin_ac, limit=None, approved=approved, archived=archived, code=code, serialized=False)
    clearance_objects = []
    # print(type(sections[0]['approvals']))
    if len(sections):
        clearance_objects = sections[0]['approvals']
    paginated_queryset = paginator.paginate_queryset(clearance_objects, request)

    serializer = Serializer_class(paginated_queryset, many=True)
    response = paginator.get_paginated_response(serializer.data)
    return response

@api_view()
def dept_sections(request):
    return Response(get_dept_sections())

@api_view(['POST'])
def assign_member(request):
    try:
        role = request.data['role']
        code = request.data['code']
        user_id = request.data['user_id']
    except Exception as e:
        return Response({'details': 'Data missing'}, status=status.HTTP_400_BAD_REQUEST)
    target_user = get_object_or_404(AdminAccount, pk=user_id)
    if role == 'administrative':
        admins_qs = AdminAccount.objects.filter(user_type=code)
        admins_qs.update(user_type='general')
        target_user.user_type = code
        target_user.save()
    elif role in ['dept_head', 'dept_clerk']:
        dept = get_object_or_404(Department, codename=code)
        if role == 'dept_head':
            dept.head = target_user
        elif role == 'dept_clerk' and dept.dept_type == 'administrative':
            dept.clerk = target_user
        dept.save()
    elif role == 'lab_incharge':
        lab = get_object_or_404(Lab, codename=code)
        lab.incharge = target_user
        lab.save()
    else:
        return Response({'details': 'No action to perform'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'info': 'Member Assigned'})