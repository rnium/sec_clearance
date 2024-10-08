import uuid
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from clearance.models import Department, Session
from django.utils import timezone
from django.core.exceptions import ValidationError
from solo.models import SingletonModel


account_types = (
    ('principal', 'Principal'),
    ('academic', 'Academic Section'),
    ('cashier', 'Cash Section'),
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
        return self.expiration >= timezone.now()


class BaseAccount(models.Model):
    phone = models.CharField(null=True, blank=True, max_length=15)
    profile_picture = models.ImageField(upload_to="profiles/dp/",
                                        null=True, 
                                        blank=True,
                                        validators=[FileExtensionValidator(allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS)])
    class Meta:
        abstract = True

    def clean(self):
        if self.phone is not None:
            if not self.phone.isdigit():
                raise ValidationError("Invalid phone number")
            if len(self.phone) != 11:
                raise ValidationError("Phone number needs to be 11 digits long")
        super().clean()
    
    @property
    def avatar_url(self):
        if bool(self.profile_picture):
            return self.profile_picture.url
        else:
            return static('clearance/images/blank-dp.svg')


class AdminAccount(BaseAccount):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_super_admin = models.BooleanField(default=False)
    dept = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
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
        depts = self.department_set.all().order_by('id')
        return depts
            
    @property
    def labs_incharge(self):
        labs = self.lab_set.all()
        return labs    
            
    @property
    def dept_clerks(self):
        clerks = Department.objects.filter(clerk=self)
        return clerks


class StudentPlaceholder(models.Model):
    registration = models.IntegerField(primary_key=True, unique=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ["registration"]
       

class StudentAccount(BaseAccount):
    registration = models.IntegerField(primary_key=True, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    hall = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        ordering = ["registration"]
    
    def __str__(self):
        return str(self.registration)
    
    def clean(self):
        if self.hall is not None:
            if self.hall.dept_type != 'hall':
                raise ValidationError("Department Type needs to be Hall")
        super().clean()
        
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
        elif not self.clearance.is_approved or self.clearance.progress < 100:
            return 3
        elif self.clearance.is_approved:
            return 4
        else:
            return 0
        
        
class StudentNotice(SingletonModel):
    notice = models.CharField(max_length=1000, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)