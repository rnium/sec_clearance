from clearance.api.serializer import AdministrativeApprovalSerializer, DeptApprovalSerializer, ClerkApprovalSerializer, LabApprovalSerializer
from clearance.models import (Department, Lab, Clearance, 
                              AdministrativeApproval, DeptApproval, LabApproval, ClerkApproval)

def create_clearance_entities(student):
    clearance, created = Clearance.objects.get_or_create(student=student)
    # administrative roles
    for role in AdministrativeApproval._meta.get_field('admin_role').choices:
        approval, created = AdministrativeApproval.objects.get_or_create(clearance=clearance, admin_role=role[0])
    # academic and accessory dept
    academic_depts = Department.objects.exclude(dept_type='administrative')
    for dept in academic_depts:
        dept_approval, created = DeptApproval.objects.get_or_create(clearance=clearance, dept=dept)
        for lab in dept.lab_set.all():
            lab_approval, created = LabApproval.objects.get_or_create(clearance=clearance, lab=lab, dept_approval=dept_approval)
    # administrative dept
    administrative_depts = Department.objects.filter(dept_type='administrative')
    for dept in administrative_depts:
        dept_approval, created = DeptApproval.objects.get_or_create(clearance=clearance, dept=dept)
        clerk_approval, created = ClerkApproval.objects.get_or_create(clearance=clearance, dept_approval=dept_approval)


def get_administrative_clearance_requests(admin_ac, limit=None, approved=False, archived=False):
    approvals = []
    if (admin_ac.user_type not in [utype[0] for utype in AdministrativeApproval._meta.get_field('admin_role').choices]):
        return approvals
    approvals_qs = AdministrativeApproval.objects.filter(admin_role=admin_ac.user_type, is_approved=approved, is_archived=archived)
    count = 0
    for app_req in approvals_qs:
        count += 1
        if app_req.approval_seekable:
            serializer = AdministrativeApprovalSerializer(app_req)
            approvals.append(serializer.data)
        if type(limit) == int and count >= limit:
            break
    section = {
        'type': 'administrative',
        'title': admin_ac.get_user_type_display(),
        'approvals': approvals
    }
    return [section]


def get_dept_head_clearance_requests(admin_ac, limit=None, approved=False, archived=False):
    approvals = []
    approvals_qs = DeptApproval.objects.filter(dept__head=admin_ac, is_approved=approved, is_archived=archived)
    for dept in Department.objects.all():
        dept_approval_qs = approvals_qs.filter(dept=dept)
        seekable_approvals = []
        for approval in dept_approval_qs:
            if approval.approval_seekable:
                seekable_approvals.append(approval)
        if type(limit) == int:
            seekable_approvals = seekable_approvals[:limit]
        if len(seekable_approvals):
            serializer = DeptApprovalSerializer(seekable_approvals, many=True)
            approvals.append(
                {
                    'type': 'dept_head',
                    'title': dept.name,
                    'approvals': serializer.data
                }
            )
    return approvals


def get_dept_clerk_clearance_requests(admin_ac, limit=None, approved=False, archived=False):
    approvals = []
    approvals_qs = ClerkApproval.objects.filter(dept_approval__dept__clerk=admin_ac, is_approved=approved, is_archived=archived)
    for dept in Department.objects.all():
        clerk_approval_qs = approvals_qs.filter(dept_approval__dept=dept)
        if type(limit) == int:
            clerk_approval_qs = clerk_approval_qs[:limit]
        if clerk_approval_qs.count():
            serializer = ClerkApprovalSerializer(clerk_approval_qs, many=True)
            approvals.append(
                {
                    'type': 'dept_clerk',
                    'title': dept.name,
                    'approvals': serializer.data
                }
            )
    return approvals


def get_lab_incharge_clearance_requests(admin_ac, limit=None, approved=False, archived=False):
    approvals = []
    approvals_qs = LabApproval.objects.filter(lab__incharge=admin_ac, is_approved=approved, is_archived=archived)
    for lab in Lab.objects.all():
        lab_approval_qs = approvals_qs.filter(lab=lab)
        if type(limit) == int:
            lab_approval_qs = lab_approval_qs[:limit]
        if lab_approval_qs.count():
            serializer = LabApprovalSerializer(lab_approval_qs, many=True)
            approvals.append(
                {
                    'type': 'dept_lab',
                    'title': str(lab),
                    'approvals': serializer.data
                }
            )
    return approvals
