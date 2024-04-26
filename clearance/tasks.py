from celery import shared_task
from clearance.api.utils import get_admin_dashboard_stats_data
from accounts.models import AdminAccount


@shared_task
def send_email_notifications():
    with open('notif.txt', 'w') as f:
        f.write("print('notification sent! asd', flush=1)")