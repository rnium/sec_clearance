from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from accounts.models import AdminAccount, StudentAccount
from accounts.serializer import AdminAccountSerializer
from clearance.models import Department, DeptApproval, ClerkApproval
from pathlib import Path
from PIL import Image
from io import BytesIO
from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404


def validate_image_extension(value):
    valid_extensions = ['.'+n for n in settings.ALLOWED_IMAGE_EXTENSIONS]
    ext = Path(value.name).suffix
    if not ext.lower() in valid_extensions:
        raise ValidationError('Invalid file type. Allowed file types are: {}'.format(', '.join(valid_extensions)))


def compress_image(image):
    try:
        validate_image_extension(image)
    except ValidationError as e:
        raise ValidationError(e)
    img = Image.open(image)
    width, height = img.size
    # Calculate the dimensions of the center portion to be cropped
    crop_width = crop_height = min(width, height)

    # Calculate the left, upper, right, and lower coordinates of the center portion
    left = (width - crop_width) // 2
    upper = (height - crop_height) // 2
    right = left + crop_width
    lower = upper + crop_height

    # Crop the center portion of the image
    center_cropped_image = img.crop((left, upper, right, lower))
    formatted_img = center_cropped_image.resize((500,500))
    img_format = img.format.lower()
    img_io = BytesIO()
    formatted_img.save(img_io, format=img_format, quality=50)
    img_file = ContentFile(img_io.getvalue())

    if hasattr(image, 'name') and image.name:
        img_file.name = image.name

    if hasattr(image, 'content_type') and image.content_type:
        img_file.content_type = image.content_type

    if hasattr(image, 'size') and image.size:
        img_file.size = image.size

    if hasattr(image, 'charset') and image.charset:
        img_file.charset = image.charset

    if hasattr(image, '_committed') and image._committed:
        img_file._committed = image._committed

    return img_file


def get_userinfo_data(user):
    data = {
        'is_authenticated': False,
        'username': '',
        'user_fullname': '',
        'account_type': '',
        'avatar_url': '',
        'user_type': '',
        'is_superadmin': False,
    }
    if user.is_authenticated:
        data['is_authenticated'] = True
        data['username'] = user.get_username()
    if hasattr(user, 'adminaccount'):
        admin_ac = user.adminaccount
        data['account_type'] = 'admin'
        data['user_type'] = admin_ac.user_type
        data['user_fullname'] = admin_ac.full_name
        data['avatar_url'] = admin_ac.avatar_url
        data['is_superadmin'] = admin_ac.is_super_admin
    elif hasattr(user, 'studentaccount'):
        student_ac = user.studentaccount
        data['account_type'] = 'student'
        data['user_fullname'] = student_ac.full_name
        data['avatar_url'] = student_ac.avatar_url
    return data

    
def get_amdin_roles(admin_ac):
    roles = []
    if admin_ac.user_type in [utype[0] for utype in admin_ac._meta.get_field('user_type').choices[:3]]:
        roles.append(
            {
                'type': 'administrative',
                'code': 'admin',
                'title': admin_ac.get_user_type_display(),
            }
        )
    for dept in admin_ac.head_of_the_departments:
        roles.append(
            {
                'type': 'dept_head',
                'code': dept.codename,
                'title': dept.name,
            }
        )
    for dept in admin_ac.dept_clerks:
        roles.append(
            {
                'type': 'dept_clerk',
                'code': dept.codename,
                'title': dept.name,
            }
        )
    for lab in admin_ac.labs_incharge:
        roles.append(
            {
                'type': 'lab_incharge',
                'code': lab.codename,
                'title': str(lab),
            }
        )
    
    return roles


def get_members_data():
    data = []
    ac_qs = AdminAccount.objects.all()
    section = {'title': 'Administration', 'accounts': []}
    admin_acs = [
        *list(ac_qs.filter(user_type='principal')),
        *list(ac_qs.filter(user_type='academic')),
    ]
    for admin_ac in admin_acs:
        if admin_ac:
            serializer = AdminAccountSerializer(admin_ac)
            section['accounts'].append(serializer.data)
    data.append(section)
    for dept in Department.objects.all():
        dept_acs = sorted(list(ac_qs.filter(dept=dept)), key=lambda ac: ac.department_set.all().count(), reverse=True)
        section = {'title': dept.display_name, 'accounts': []}
        if len(dept_acs):
            serializer = AdminAccountSerializer(dept_acs, many=True)
            section['accounts'].extend(serializer.data)
        data.append(section)
    section = {'title': 'Cash Section', 'accounts': []}
    admin_acs = ac_qs.filter(user_type='cashier')
    for admin_ac in admin_acs:
        if admin_ac:
            serializer = AdminAccountSerializer(admin_ac)
            section['accounts'].append(serializer.data)
    data.append(section)
    undesignated_admins = ac_qs.filter(dept=None, user_type='general')
    section = {'title': 'Undesignated Users', 'accounts': []}
    if undesignated_admins.count():
        serializer = AdminAccountSerializer(undesignated_admins, many=True)
        section['accounts'].extend(serializer.data)
    data.append(section)
    return data


def adapt_hall_change_to_clearancce(clearance, prev_hall, new_hall):
    if prev_hall:
        hall_dept_approval = DeptApproval.objects.filter(clearance=clearance, dept=prev_hall)
        hall_dept_approval.delete()
    if new_hall:
        h_approval, created = DeptApproval.objects.get_or_create(clearance=clearance, dept=new_hall)
        clerk_approval, created = ClerkApproval.objects.get_or_create(clearance=clearance, dept_approval=h_approval)
    clearance.update_stats()
        

def update_student_profile_as_admin(data):
    student = get_object_or_404(StudentAccount, registration=data.get('registration'))
    user = student.user
    fname = data.get('first_name')
    lname = data.get('last_name')
    user_updatable = False
    if fname and fname != user.first_name:
        user.first_name = fname
        user_updatable = True
    if lname and lname != user.last_name:
        user.last_name = lname
        user_updatable = True
    if user_updatable:
        user.save()
    new_hall = Department.objects.filter(dept_type='hall', pk=data.get('hall_id')).first()
    if student.hall != new_hall:
        prev_hall = student.hall
        student.hall = new_hall
        student.save()
        if hasattr(student, 'clearance'):
            adapt_hall_change_to_clearancce(student.clearance, prev_hall, new_hall)