from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandError
from clearance.models import Department, Lab
from django_celery_beat.models import PeriodicTask, CrontabSchedule


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='4',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*'
        )
        
        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='Sending notification',
            task='clearance.tasks.send_email_notifications',
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"PeriodicTask Created"))
