from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from accounts.models import AdminAccount
from accounts.serializer import AdminAccountSerializer
from clearance.models import Department
from pathlib import Path
from PIL import Image
from io import BytesIO
from django.conf import settings
from django.core.exceptions import ValidationError


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
    section = {'title': 'Administrator', 'accounts': []}
    admin_acs = [
        *list(ac_qs.filter(user_type='principal')),
        *list(ac_qs.filter(user_type='academic')),
        *list(ac_qs.filter(user_type='cashier'))
    ]
    for admin_ac in admin_acs:
        if admin_ac:
            serializer = AdminAccountSerializer(admin_ac)
            section['accounts'].append(serializer.data)
    data.append(section)
    for dept in Department.objects.all():
        dept_acs = ac_qs.filter(dept=dept)
        section = {'title': dept.display_name, 'accounts': []}
        if dept_acs.count():
            serializer = AdminAccountSerializer(dept_acs, many=True)
            section['accounts'].extend(serializer.data)
        data.append(section)
    undesignated_admins = ac_qs.filter(dept=None, user_type='general')
    section = {'title': 'Undesignated Users', 'accounts': []}
    if undesignated_admins.count():
        serializer = AdminAccountSerializer(undesignated_admins, many=True)
        section['accounts'].extend(serializer.data)
    data.append(section)
    return data