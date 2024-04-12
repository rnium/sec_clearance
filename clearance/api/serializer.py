from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from clearance.models import Clearance, AdministrativeApproval, DeptApproval, ClerkApproval, LabApproval
from accounts.serializer import StudentAccountSerializer
from django.urls import reverse

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
        
        