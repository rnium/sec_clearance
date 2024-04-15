from django.db import models
from clearance.utils import get_ordinal_number


class Department(models.Model):
    dept_types = (
        ('academic', 'Academic Dept'),
        ('accessory', 'Accessory Dept'),
        ('administrative', 'Administrative'),
    )
    codename = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)
    dept_type = models.CharField(choices=dept_types, max_length=50)
    head = models.ForeignKey('accounts.AdminAccount', null=True, blank=True, on_delete=models.SET_NULL)
    clerk = models.ForeignKey('accounts.AdminAccount', null=True, blank=True, on_delete=models.SET_NULL, related_name='clerk')
    added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Lab(models.Model):
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    codename = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    incharge = models.ForeignKey('accounts.AdminAccount', null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self) -> str:
        return f"{self.name}, {self.dept.codename.upper()}"


class Session(models.Model):
    from_year = models.IntegerField()
    to_year = models.IntegerField()
    batch_no = models.IntegerField()
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ["-from_year"]
        constraints = [
            models.UniqueConstraint(fields=["from_year", "dept"], name="unique_dept_session"),
            models.UniqueConstraint(fields=["batch_no", "dept"], name="unique_dept_batch"),
        ]
        
    def __str__(self):
        return f"{self.dept.codename.upper()} {self.session_code}"
    
            
    @property
    def session_code(self):
        return f"{self.from_year}-{self.to_year % 2000}"
    
    @property
    def session_code_formal(self):
        return f"{(self.from_year % 2000) + 2000}-{(self.to_year % 2000) + 2000}"

    @property
    def batch_name(self):
        return f"{self.dept.name.upper()} {get_ordinal_number(self.batch_no)} batch"


class Clearance(models.Model):
    student = models.OneToOneField('accounts.StudentAccount', on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    progress = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def update_stats(self, *args, **kwargs):
        admin_app_qs = self.administrativeapproval_set.all()
        dept_app_qs = self.deptapproval_set.all()
        clerk_app_qs = self.clerkapproval_set.all()
        lab_app_qs = self.labapproval_set.all()
        admin_app_qs_approved = admin_app_qs.filter(is_approved=True)
        dept_app_qs_approved = dept_app_qs.filter(is_approved=True)
        clerk_app_qs_approved = clerk_app_qs.filter(is_approved=True)
        lab_app_qs_approved = lab_app_qs.filter(is_approved=True)
        total_approvals = admin_app_qs.count() + dept_app_qs.count() + clerk_app_qs.count() + lab_app_qs.count()
        approved_approvals = (admin_app_qs_approved.count() + dept_app_qs_approved.count() 
                              + clerk_app_qs_approved.count() + lab_app_qs_approved.count())
        percent_progress = 0
        if total_approvals:
            percent_progress = round(((approved_approvals/total_approvals) * 100), 2)
        self.progress = percent_progress
        if percent_progress == 100:
            self.is_approved = True
        self.save(*args, **kwargs)
        

class BaseApproval(models.Model):
    clearance = models.ForeignKey(Clearance, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    approved_by = models.ForeignKey('accounts.AdminAccount', null=True, blank=True, on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.clearance.update_stats()


class AdministrativeApproval(BaseApproval):
    administrative_roles = (
        ('principal', 'Principal'),
        ('academic', 'SEC Academic'),
        ('cashier', 'Cashier'),
    )
    admin_role = models.CharField(choices=administrative_roles, max_length=50)
    
    class Meta:
        ordering = ['clearance__added_at']
        constraints = [
            models.UniqueConstraint(fields=['clearance', 'admin_role'], name='unique_adminrole_per_clearance')
        ]

        
    def __str__(self):
         return f"{self.get_admin_role_display()} Approval for {self.clearance.id}"
     
    @property
    def approval_seekable(self):
        pending_depts = self.clearance.deptapproval_set.filter(is_approved=False)
        pending_clerks = self.clearance.clerkapproval_set.filter(is_approved=False)
        pending_labs = self.clearance.labapproval_set.filter(is_approved=False)
        if pending_depts.count() or pending_labs.count() or pending_clerks.count():
            return False
        if self.admin_role in ['principal', 'cashier']:
            return True
        else:
            other_admin_approvals = self.clearance.administrativeapproval_set.filter(is_approved=False).exclude(admin_role='academic')
            return not bool(other_admin_approvals.count())


class DeptApproval(BaseApproval):
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    
    class Meta:
        ordering = ['clearance__added_at']
        constraints = [
            models.UniqueConstraint(fields=['dept', 'clearance'], name='unique_dept_approval_per_clearance')
        ]
        
    @property
    def approval_seekable(self):
        pending_labs = self.clearance.labapproval_set.filter(is_approved=False)
        pending_clerks = self.clearance.clerkapproval_set.filter(is_approved=False)
        if pending_labs.count() or pending_clerks.count():
            return False
        return True

    def __str__(self):
         return f"{self.dept} DeptApproval for {self.clearance.id}"


class ClerkApproval(BaseApproval):
    dept_approval = models.ForeignKey(DeptApproval, on_delete=models.CASCADE)
    owed = models.IntegerField(default=0)
    
    
    class Meta:
        ordering = ['clearance__added_at']
        constraints = [
            models.UniqueConstraint(fields=['dept_approval', 'clearance'], name='unique_clerk_approval_per_clearance')
        ]
        
    def __str__(self):
         return f"{self.dept_approval.dept} ClerkApproval for {self.clearance.id}"

    
class LabApproval(BaseApproval):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    dept_approval = models.ForeignKey(DeptApproval, on_delete=models.CASCADE)
    owed = models.IntegerField(default=0)
    
    
    class Meta:
        ordering = ['clearance__added_at']
        constraints = [
            models.UniqueConstraint(fields = ['lab', 'clearance'], name='unique_lab_approval_per_clearance')
        ]
    
    def __str__(self):
         return f"{self.lab} LabApproval for {self.clearance.id}"

    