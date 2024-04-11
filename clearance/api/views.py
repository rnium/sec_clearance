from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.utils import get_userinfo_data
from accounts.models import StudentAccount, AdminAccount
from clearance.api.utils import (create_clearance_entities, get_administrative_clearance_requests, 
                                 get_dept_head_clearance_requests, get_dept_clerk_clearance_requests, 
                                 get_lab_incharge_clearance_requests)
from clearance.apps import get_model_by_name
from django.shortcuts import get_object_or_404
from django.utils import timezone

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
        return Response({'info': 'clearance already archived'}, status=status.HTTP_400_BAD_REQUEST)
    clearance_req.is_archived = True
    clearance_req.save()
    return Response({'info': 'Clearance Request Archived'})