from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from clearance.models import (Department, Session, Clearance, AdministrativeApproval, 
                              DeptApproval, ClerkApproval, LabApproval)
from accounts.serializer import StudentAccountSerializer
from django.urls import reverse


class DepartmentSeializer(ModelSerializer):
    class Meta:
        model = Department
        exclude = ['head', 'clerk', 'added']


class SessionSeializer(ModelSerializer):
    session_code = serializers.SerializerMethodField()
    class Meta:
        model = Session
        fields = ['id', 'session_code']
    def get_session_code(self, obj):
        return obj.session_code


class ClearanceBasicSerializer(ModelSerializer):
    student = StudentAccountSerializer()
    adminstrative = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    # dept_clerk = serializers.SerializerMethodField()
    # lab_incharge = serializers.SerializerMethodField()
    
    class Meta:
        model = Clearance
        fields = "__all__"
        
    def get_adminstrative(self, obj):
        s = AdministrativeApprovalBasicSerializer(obj.administrativeapproval_set.all(), many=True)
        return s.data
        
    def get_department(self, obj):
        s = DeptApprovalBasicSerializer(obj.deptapproval_set.all(), many=True)
        return s.data
        
    # def get_dept_clerk(self, obj):
    #     s = ClerkApprovalBasicSerializer(obj.clerkapproval_set.all(), many=True)
    #     return s.data
        
    # def get_lab_incharge(self, obj):
    #     s = LabApprovalBasicSerializer(obj.labapproval_set.all(), many=True)
    #     return s.data


class ClearanceBasicApprovalSerializerBase(ModelSerializer):
    title = serializers.SerializerMethodField()
    is_seekable = serializers.SerializerMethodField()
    class Meta:
        model = None
        exclude = ['clearance']


class AdministrativeApprovalBasicSerializer(ClearanceBasicApprovalSerializerBase):
    class Meta(ClearanceBasicApprovalSerializerBase.Meta):
        model = AdministrativeApproval
    def get_title(self, obj):
        return obj.get_admin_role_display()
    def get_is_seekable(self, obj):
        return obj.approval_seekable


class DeptApprovalBasicSerializer(ClearanceBasicApprovalSerializerBase):
    clerk_approval = serializers.SerializerMethodField()
    lab_approval = serializers.SerializerMethodField()
    class Meta(ClearanceBasicApprovalSerializerBase.Meta):
        model = DeptApproval
    def get_title(self, obj):
        return f"Head of {obj.dept.display_name}"
    def get_is_seekable(self, obj):
        return obj.approval_seekable
    def get_clerk_approval(self, obj):
        s = ClerkApprovalBasicSerializer(obj.clerkapproval_set.all(), many=True)
        return s.data
    def get_lab_approval(self, obj):
        s = LabApprovalBasicSerializer(LabApproval.objects.filter(clearance=obj.clearance, lab__dept=obj.dept), many=True)
        return s.data


class ClerkApprovalBasicSerializer(ClearanceBasicApprovalSerializerBase):
    class Meta(ClearanceBasicApprovalSerializerBase.Meta):
        model = ClerkApproval
    def get_title(self, obj):
        return f"Clerk of {obj.dept_approval.dept.display_name}"
    def get_is_seekable(self, obj):
        return True


class LabApprovalBasicSerializer(ClearanceBasicApprovalSerializerBase):
    class Meta(ClearanceBasicApprovalSerializerBase.Meta):
        model = LabApproval
    def get_title(self, obj):
        return f"In charge of {obj.lab.name}"
    def get_is_seekable(self, obj):
        return True


class PendingClearanceSerializer(ModelSerializer):
    student = StudentAccountSerializer()
    class Meta:
        model = Clearance
        fields = ['progress', 'added_at', 'student']


class PendingSerializerBase(ModelSerializer):
    applied_at = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    session = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    registration = serializers.SerializerMethodField()
    approval_url = serializers.SerializerMethodField()
    archive_url = serializers.SerializerMethodField()
    unarchive_url = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    class Meta:
        model = None
        exclude = ['clearance', 'is_approved', 'approved_by']

    def get_applied_at(self, obj):
        return obj.clearance.added_at
    def get_progress(self, obj):
        return obj.clearance.progress
    def get_session(self, obj):
        return str(obj.clearance.student.session)
    def get_name(self, obj):
        return str(obj.clearance.student.full_name)
    def get_registration(self, obj):
        return str(obj.clearance.student.registration)
    def get_approval_url(self, obj):
        return reverse('clearance:approve_clearance_entity', args=(obj._meta.model_name, obj.id))
    def get_archive_url(self, obj):
        return reverse('clearance:archive_clearance_entity', args=(obj._meta.model_name, obj.id))
    def get_unarchive_url(self, obj):
        return reverse('clearance:unarchive_clearance_entity', args=(obj._meta.model_name, obj.id))
    def get_avatar_url(self, obj):
        return obj.clearance.student.avatar_url

class AdministrativeApprovalSerializer(PendingSerializerBase):
    class Meta(PendingSerializerBase.Meta):
        model = AdministrativeApproval

        
class DeptApprovalSerializer(PendingSerializerBase):
    class Meta(PendingSerializerBase.Meta):
        model = DeptApproval
 
class ClerkApprovalSerializer(PendingSerializerBase):
    class Meta(PendingSerializerBase.Meta):
        model = ClerkApproval


class LabApprovalSerializer(PendingSerializerBase):
    class Meta(PendingSerializerBase.Meta):
        model = LabApproval
        
        