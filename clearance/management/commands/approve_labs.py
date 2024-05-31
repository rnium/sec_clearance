from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandError
from clearance.models import Department, Lab, Clearance, DeptApproval, ClerkApproval, LabApproval
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils import timezone


def approve_clerks_and_labs(reg):
    clearance = Clearance.objects.get(student__registration=reg)
    clerk_appr_qs = ClerkApproval.objects.filter(clearance=clearance)
    for appr in clerk_appr_qs:
        clerk = appr.dept_approval.dept.clerk
        appr.is_approved = True
        appr.approved_by = clerk
        appr.approved_at = timezone.now()
        appr.save()
    lab_appr_qs = LabApproval.objects.filter(clearance=clearance)
    for appr in lab_appr_qs:
        incharge = appr.lab.incharge
        appr.is_approved = True
        appr.approved_by = incharge
        appr.approved_at = timezone.now()
        appr.save()
    clearance.update_stats()
        
    

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        try:
            approve_clerks_and_labs(2018338547)
            self.stdout.write(self.style.SUCCESS(f"Complete"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
