from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandError
from clearance.models import Department, Lab, Clearance, DeptApproval, ClerkApproval, LabApproval
from django_celery_beat.models import PeriodicTask, CrontabSchedule


def migrate_lab(from_dept, to_lab):
    dept = Department.objects.get(codename=from_dept)
    lab = Lab.objects.get(codename=to_lab)
    lab.incharge = dept.clerk
    lab.save()
    clerk_app_qs = ClerkApproval.objects.filter(dept_approval__dept=dept)
    updatable_clearances = [] 
    for c_app in clerk_app_qs:
        d_app, _ = DeptApproval.objects.get_or_create(clearance=c_app.clearance, dept=lab.dept)
        l_app, _ = LabApproval.objects.get_or_create(clearance=c_app.clearance, lab=lab, dept_approval=d_app)
        l_app.is_approved = c_app.is_approved
        l_app.approved_by = c_app.approved_by
        l_app.approved_at = c_app.approved_at
        l_app.save()
        updatable_clearances.append(c_app.clearance)
    dept.delete()
    for clr in updatable_clearances:
        clr.update_stats()


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        try:
            migrate_lab('central_computer_center', 'central_computer_center')
            self.stdout.write(self.style.SUCCESS(f"Complete"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
