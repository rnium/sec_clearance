from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandError
from clearance.models import Department, Lab
from django_celery_beat.models import PeriodicTask, CrontabSchedule


def get_or_create_schedule(minute='*', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'):
    email_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=minute,
        hour=hour,
        day_of_week=day_of_week,
        day_of_month=day_of_month,
        month_of_year=month_of_year
    )
    return email_schedule


def create_task(command, crontab: CrontabSchedule, name:str, task:str):
    task, created = PeriodicTask.objects.get_or_create(
        crontab=crontab,
        name=name,
        task=task,
    )
    if created:
        command.stdout.write(command.style.SUCCESS(f"'{name}' Task Created"))
            

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        email_schedule = get_or_create_schedule('0', '15')
        general_admin_sms_schedule = get_or_create_schedule('0', '4')
        dept_head_sms_schedule = get_or_create_schedule('0', '6')
        cashier_sms_schedule = get_or_create_schedule('0', '8')
        principal_sms_schedule = get_or_create_schedule('0', '10')
        academic_sms_schedule = get_or_create_schedule('0', '14')
        
        tasks = [
             {
                'crontab': email_schedule,
                'name': 'Sending notification email',
                'task': 'clearance.tasks.send_email_notifications'
            },
            {
                'crontab': general_admin_sms_schedule,
                'name': 'Sending General Admin SMS',
                'task': 'clearance.tasks.send_general_user_sms'
            },
            {
                'crontab': dept_head_sms_schedule,
                'name': 'Sending Dept Head SMS',
                'task': 'clearance.tasks.send_dept_head_sms'
            },
            {
                'crontab': cashier_sms_schedule,
                'name': 'Sending Cashier SMS',
                'task': 'clearance.tasks.send_cashier_sms'
            },
            {
                'crontab': principal_sms_schedule,
                'name': 'Sending Principal SMS',
                'task': 'clearance.tasks.send_principal_sms'
            },
            {
                'crontab': academic_sms_schedule,
                'name': 'Sending SEC Academic SMS',
                'task': 'clearance.tasks.send_sec_academic_sms'
            },
        ]
        
        for task in tasks:
            create_task(self, **task)

