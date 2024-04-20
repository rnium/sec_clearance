from clearance.api.serializer import (AdministrativeApprovalSerializer, DeptApprovalSerializer, 
                                      ClerkApprovalSerializer, LabApprovalSerializer,
                                      SessionSeializer)
from clearance.models import (Department, Lab, Session, Clearance, 
                              AdministrativeApproval, DeptApproval, LabApproval, ClerkApproval)
from accounts.models import administrative_account_types
from accounts.models import AdminAccount
from accounts.serializer import AdminAccountBasicSerializer
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils import timezone

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


def get_administrative_clearance_requests(admin_ac, limit=None, approved=False, archived=False, code=None, serialized=True):
    approvals = []
    if (admin_ac.user_type not in [utype[0] for utype in AdministrativeApproval._meta.get_field('admin_role').choices]):
        return approvals
    approvals_qs = AdministrativeApproval.objects.filter(admin_role=admin_ac.user_type, is_approved=approved, is_archived=archived)
    if approved:
        approvals_qs = approvals_qs.order_by('-approved_at')
    count = 0
    for app_req in approvals_qs:
        count += 1
        if app_req.approval_seekable:
            if serialized:
                serializer = AdministrativeApprovalSerializer(app_req)
                approvals.append(serializer.data)
            else:
                approvals.append(app_req)
        if type(limit) == int and count >= limit:
            break
    section = {
        'type': 'administrative',
        'title': admin_ac.get_user_type_display(),
        'approvals': approvals
    }
    if len(approvals) == 0:
        return []
    return [section]


def get_dept_head_clearance_requests(admin_ac, limit=None, approved=False, archived=False, code=None, serialized=True):
    approvals = []
    approvals_qs = DeptApproval.objects.filter(dept__head=admin_ac, is_approved=approved, is_archived=archived)
    if code:
        departments = Department.objects.filter(codename=code)
    else:
        departments = Department.objects.all()
    for dept in departments:
        dept_approval_qs = approvals_qs.filter(dept=dept)
        if approved:
            dept_approval_qs = dept_approval_qs.order_by('-approved_at')
        seekable_approvals = []
        for approval in dept_approval_qs:
            if approval.approval_seekable:
                seekable_approvals.append(approval)
        if type(limit) == int:
            seekable_approvals = seekable_approvals[:limit]
        if len(seekable_approvals):
            if serialized:
                serializer = DeptApprovalSerializer(seekable_approvals, many=True)
                seekable_approvals = serializer.data
            approvals.append(
                {
                    'type': 'dept_head',
                    'title': f"{dept.head_title} of {dept.name}",
                    'approvals': seekable_approvals
                }
            )
    return approvals


def get_dept_clerk_clearance_requests(admin_ac, limit=None, approved=False, archived=False, code=None, serialized=True):
    approvals = []
    approvals_qs = ClerkApproval.objects.filter(dept_approval__dept__clerk=admin_ac, is_approved=approved, is_archived=archived)
    if code:
        departments = Department.objects.filter(codename=code)
    else:
        departments = Department.objects.all()
    for dept in departments:
        clerk_approval_qs = approvals_qs.filter(dept_approval__dept=dept)
        if approved:
            clerk_approval_qs = clerk_approval_qs.order_by('-approved_at')
        if type(limit) == int:
            clerk_approval_qs = clerk_approval_qs[:limit]
        if clerk_approval_qs.count():
            clerk_approvals = clerk_approval_qs
            if serialized:
                serializer = ClerkApprovalSerializer(clerk_approval_qs, many=True)
                clerk_approvals = serializer.data
            approvals.append(
                {
                    'type': 'dept_clerk',
                    'title': f"{dept.clerk_title} of {dept.name}",
                    'approvals': clerk_approvals
                }
            )
    return approvals


def get_lab_incharge_clearance_requests(admin_ac, limit=None, approved=False, archived=False, code=None, serialized=True):
    approvals = []
    approvals_qs = LabApproval.objects.filter(lab__incharge=admin_ac, is_approved=approved, is_archived=archived)
    if code:
        all_labs = Lab.objects.filter(codename=code)
    else:
        all_labs = Lab.objects.all()
    for lab in all_labs:
        lab_approval_qs = approvals_qs.filter(lab=lab)
        if approved:
            lab_approval_qs = lab_approval_qs.order_by('-approved_at')
        if type(limit) == int:
            lab_approval_qs = lab_approval_qs[:limit]
        if lab_approval_qs.count():
            lab_approvals = lab_approval_qs
            if serialized:
                serializer = LabApprovalSerializer(lab_approval_qs, many=True)
                lab_approvals = serializer.data
            approvals.append(
                {
                    'type': 'lab_incharge',
                    'title': str(lab),
                    'approvals': lab_approvals
                }
            )
    return approvals


def get_entity_data(title, entity_type, code, admin_ac=None):
    data = {
        'title': title,
        'type': entity_type,
        'code': code,
        'incharge_user': None
    }
    if admin_ac:
        serializer = AdminAccountBasicSerializer(admin_ac)
        data['incharge_user'] = serializer.data
    return data
        

def get_administration_dept_data():
    data = {
        'title': "Administration",
        'entities': []
    }
    principal = AdminAccount.objects.filter(user_type='principal').first()
    academic = AdminAccount.objects.filter(user_type='academic').first()
    cashier = AdminAccount.objects.filter(user_type='cashier').first()
    if principal:
        data['entities'].append(get_entity_data(principal.get_user_type_display(), 'administrative', 'principal', principal))
    else:
        data['entities'].append(get_entity_data('Principal', 'administrative', 'principal'))
    if academic:
        data['entities'].append(get_entity_data(academic.get_user_type_display(), 'administrative', 'academic', academic))
    else:
        data['entities'].append(get_entity_data('SEC Academic', 'administrative', 'academic'))
    if cashier:
        data['entities'].append(get_entity_data(cashier.get_user_type_display(), 'administrative', 'cashier', cashier))
    else:
        data['entities'].append(get_entity_data('Cashier', 'administrative', 'cashier'))
    return data

def get_dept_sections():
    departments = []
    departments.append(get_administration_dept_data())
    dept_qs = Department.objects.all().order_by('id')
    for dept in dept_qs:
        data = {
            'title': dept.display_name,
            'entities': []
        }
        data['entities'].append(get_entity_data(dept.head_title, 'dept_head', dept.codename, dept.head))
        if dept.dept_type == 'administrative':
            data['entities'].append(get_entity_data(dept.clerk_title, 'dept_clerk', dept.codename, dept.clerk))
        elif dept.dept_type in ['academic', 'accessory']:
            for lab in dept.lab_set.all():
                data['entities'].append(get_entity_data(lab.name, 'lab_incharge', lab.codename, lab.incharge))
        departments.append(data)
    return departments

def unassign_member(target_user, role, code):
    if role == 'administrative':
        if target_user.user_type != code:
            raise ValidationError('User was not assigned')
        target_user.user_type = 'general'
        target_user.save()
    elif role in ['dept_head', 'dept_clerk']:
        dept = get_object_or_404(Department, codename=code)
        if role == 'dept_head':
            if target_user != dept.head:
                raise ValidationError('User is not the department head')
            dept.head = None
        elif role == 'dept_clerk' and dept.dept_type == 'administrative':
            if target_user != dept.clerk:
                raise ValidationError('User is not the department clerk')
            dept.clerk = None
        dept.save()
    elif role == 'lab_incharge':
        lab = get_object_or_404(Lab, codename=code)
        if target_user != lab.incharge:
                raise ValidationError('User is not in charge of the lab')
        lab.incharge = None
        lab.save()
    else:
        raise ValidationError('No actions to be performed!')
    
def get_dept_sessions():
    data = {}
    for dept in Department.objects.filter(dept_type='academic'):
        serializer = SessionSeializer(dept.session_set.all(), many=True)
        data[dept.codename] = serializer.data
    return data

def create_session(data):
    try:
        dept_code = data['dept']
        from_y = data['from_year']
        to_y = data['to_year']
        batch_no = data['batch_no']
    except KeyError:
        raise ValidationError("Required data missing")
    if from_y > to_y:
        raise ValidationError("'From year' must be less than 'To year'")
    dept = get_object_or_404(Department, codename=dept_code, dept_type='academic')
    session = Session.objects.create(dept=dept, from_year=from_y, to_year=to_y, batch_no=batch_no)
    return session

def get_approval_title(obj, approval_type):
    if approval_type == 'administrative':
        return obj.get_admin_role_display()
    elif approval_type == 'dept_head':
        return f"{obj.dept.head_title} of {obj.dept.display_name}"
    elif approval_type == 'dept_clerk':
        return f"{obj.dept_approval.dept.clerk_title} of {obj.dept_approval.dept.display_name}"
    elif approval_type == 'lab_incharge':
        return obj.lab.name

def post_or_get_remarks_data(model, pk, approval_type, new_remarks=None):
    app_req = get_object_or_404(model, pk=pk)
    if new_remarks:
        if app_req.is_approved:
            raise ValidationError("Cannot post in an apprroved clearance request")
        app_req.remarks = new_remarks
        app_req.remarks_added_at = timezone.now()
        app_req.save()
    return {
        'registration': app_req.clearance.student.registration,
        'title': get_approval_title(app_req, approval_type),
        'remarks_text': app_req.remarks,
    } 
    
def get_appr_remarks_data(title, appr):
    return {
        'title': title,
        'remarks': appr.remarks
    }

def get_clearance_remarks(clearance):
    remakrs = []
    if not clearance:
        return remakrs
    admin_app = clearance.administrativeapproval_set.filter(remarks__isnull=False).order_by('remarks_added_at')
    dept_head_app = clearance.deptapproval_set.filter(remarks__isnull=False).order_by('remarks_added_at')
    dept_clerk_app = clearance.clerkapproval_set.filter(remarks__isnull=False).order_by('remarks_added_at')
    lab_incharge_app = clearance.labapproval_set.filter(remarks__isnull=False).order_by('remarks_added_at')
    for app in admin_app:
        remakrs.append(get_appr_remarks_data(app.get_admin_role_display(), app))
    for app in dept_head_app:
        remakrs.append(get_appr_remarks_data(f"{app.dept.head_title} of {app.dept.display_name}", app))
    for app in dept_clerk_app:
        remakrs.append(get_appr_remarks_data(f"{app.dept_approval.dept.clerk_title} of {app.dept_approval.dept.display_name}", app))
    for app in lab_incharge_app:
        remakrs.append(get_appr_remarks_data(app.lab.name, app))
    return remakrs