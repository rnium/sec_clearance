from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes


def get_ordinal_suffix(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value
    if value % 100 in {11, 12, 13}:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(value % 10, 'th')
    return suffix

def get_ordinal_number(value):
    return f'{value}{get_ordinal_suffix(value)}'


def get_admin_roles(admin_ac):
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
                'title': f"{dept.head_title}, {dept.display_name}",
            }
        )
    for dept in admin_ac.dept_clerks:
        roles.append(
            {
                'type': 'dept_clerk',
                'code': dept.codename,
                'title': f"{dept.clerk_title}, {dept.display_name}",
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


def b64encode(data):
    return urlsafe_base64_encode(force_bytes(data))

def b64decode(data):
    return force_str(urlsafe_base64_decode(data))