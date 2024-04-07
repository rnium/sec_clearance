def get_userinfo_data(request):
    data = {
        'is_authenticated': False,
        'username': '',
        'user_fullname': '',
        'account_type': '',
        'user_type': '',
    }
    if request.user.is_authenticated:
        data['is_authenticated'] = True
    if hasattr(request.user, 'adminaccount'):
        admin_ac = request.user.adminaccount
        data['account_type'] = 'admin'
        data['user_type'] = admin_ac.user_type
        data['user_fullname'] = admin_ac.full_name
    if hasattr(request.user, 'studentaccount'):
        student_ac = request.user.studentaccount
        data['account_type'] = 'student'
        data['user_fullname'] = student_ac.full_name
    return data
    