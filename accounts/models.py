import uuid
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from clearance.models import Department, Session
from django.utils import timezone


account_types = (
    ('principal', 'Principal'),
    ('academic', 'SEC Academic'),
    ('cashier', 'Cashier'),
    ('general', 'General Admin User'),
)

administrative_account_types = [[utype][0] for utype in account_types]

class InviteToken(models.Model):
    def get_uuid():
        return uuid.uuid4().hex

    id = models.CharField(
        max_length=50,
        primary_key = True,
        default = get_uuid,
        editable = False,
    )
    from_user = models.ForeignKey(User, related_name="from_user", on_delete=models.CASCADE)
    to_user_dept_id = models.IntegerField(null=True, blank=True)
    user_email = models.EmailField()
    actype = models.CharField(max_length=10, null=True, blank=True)
    expiration = models.DateTimeField()
    
    def is_valid(self):
        return self.expiration <= timezone.now()


class BaseAccount(models.Model):
    profile_picture = models.ImageField(upload_to="profiles/dp/",
                                        null=True, 
                                        blank=True,
                                        validators=[FileExtensionValidator(allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS)])
    class Meta:
        abstract = True

    @property
    def avatar_url(self):
        if bool(self.profile_picture):
            return self.profile_picture.url
        else:
            return static('clearance/images/blank-dp.svg')


class AdminAccount(BaseAccount):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_super_admin = models.BooleanField(default=False)
    dept = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, default='general', choices=account_types)
    last_seen = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="inviting_user")
    
        
    def __str__(self):
        return self.user.username
    
    def lastseen_now(self):
        self.last_seen = timezone.now()
        self.save()
    
    @property
    def user_first_name(self):
        first_name = self.user.first_name
        if first_name:
            return first_name
        else:
            return self.user.username
    
    @property
    def full_name(self):
        first_name = self.user.first_name
        last_name = self.user.last_name
        if first_name or last_name:
            if first_name and last_name:
                return f"{first_name} {last_name}"
            elif first_name:
                return first_name
            elif last_name:
                return last_name
        else:
            return self.user.username
        
    @property
    def head_of_the_departments(self):
        depts = self.department_set.all()
        return depts
            
    @property
    def labs_incharge(self):
        labs = self.lab_set.all()
        return labs    
            
    @property
    def dept_clerks(self):
        clerks = Department.objects.filter(clerk=self)
        return clerks
        

class StudentAccount(BaseAccount):
    registration = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ["registration"]
    
    def __str__(self):
        return str(self.registration)
        
    @property
    def full_name(self):
        if self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        else:
            return self.user.first_name

    @property
    def account_state(self):
        if not self.is_approved:
            return 1
        elif not hasattr(self, 'clearance'):
            return 2
        elif not self.clearance.is_approved:
            return 3
        elif self.clearance.is_approved:
            return 4
        else:
            return 0