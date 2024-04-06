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
        return f"{self.name}, {self.dept.name}"


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
        return f"{self.dept.name.upper()} {self.session_code}"
    
            
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
    added_at = models.DateTimeField(auto_now_add=True)


class BaseApproval(models.Model):
    clearance = models.ForeignKey(Clearance, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey('accounts.AdminAccount', null=True, blank=True, on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True


class AdministrativeApproval(BaseApproval):
    administrative_roles = (
        ('principal', 'Principal'),
        ('academic', 'SEC Academic'),
        ('cashier', 'Cashier'),
    )
    admin_role = models.CharField(choices=administrative_roles, max_length=50)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['clearance', 'admin_role'], name='unique_adminrole_per_clearance')
        ]


class DeptApproval(BaseApproval):
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['dept', 'clearance'], name='unique_dept_approval_per_clearance')
        ]
        
    @property
    def approval_seekable(self):
        pending_labs = self.labapproval_set.filter(is_approved=False)
        pending_clerks = self.clerkapproval_set.filter(is_approved=False)
        if self.clearance.is_approved or pending_labs.count() or pending_clerks.count():
            return False
        return True


class ClerkApproval(BaseApproval):
    dept_approval = models.ForeignKey(DeptApproval, on_delete=models.CASCADE)
    owed = models.IntegerField(default=0)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['dept_approval', 'clearance'], name='unique_clerk_approval_per_clearance')
        ]

    
class LabApproval(BaseApproval):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    dept_approval = models.ForeignKey(DeptApproval, on_delete=models.CASCADE)
    owed = models.IntegerField(default=0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['lab', 'clearance'], name='unique_lab_approval_per_clearance')
        ]

    