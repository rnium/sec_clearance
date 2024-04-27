from celery import shared_task
from clearance.api.utils import get_admin_dashboard_stats_data
from accounts.models import AdminAccount
from accounts.mail_utils import send_admin_stats_email, send_admin_stats_sms
from django.utils import timezone


def get_mail_data(dept_data, admin_ac, mail_type='email'):
    data = {}
    data['clearances'] = 0 
    data['archives'] = 0
    data['students'] = 0
    for dept in dept_data:
        data['clearances'] += dept_data[dept]['pending']
        data['archives'] += dept_data[dept]['archived']
        if admin_ac.user_type == 'academic':
            data['students'] += dept_data[dept]['pending_students']
    if mail_type == 'email':
        is_sendabale = (data['clearances'] + data['archives'] + data['students']) > 0
    else:
        is_sendabale = (data['clearances'] + data['students']) > 0
    return (data, is_sendabale)


@shared_task
def send_email_notifications():
    admin_accounts = AdminAccount.objects.all()
    for ac in admin_accounts:
        dept_data = get_admin_dashboard_stats_data(ac)
        data, sendable = get_mail_data(dept_data, ac)
        data['current_time'] = timezone.now()
        data['admin_ac'] = ac
        if sendable:
            send_admin_stats_email(ac, data)
        data, sendable = get_mail_data(dept_data, ac, 'sms')
        if sendable:
            send_admin_stats_sms(ac, data)
            
    