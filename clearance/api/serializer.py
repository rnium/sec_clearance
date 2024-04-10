from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from clearance.models import Clearance, AdministrativeApproval, DeptApproval, ClerkApproval, LabApproval


class AdministrativeApprovalSerializer(ModelSerializer):
    class Meta:
        model = AdministrativeApproval
        fields = '__all__'

        
class DeptApprovalSerializer(ModelSerializer):
    class Meta:
        model = DeptApproval
        fields = '__all__'

 
class ClerkApprovalSerializer(ModelSerializer):
    class Meta:
        model = ClerkApproval
        fields = '__all__'


class LabApprovalSerializer(ModelSerializer):
    class Meta:
        model = LabApproval
        fields = '__all__'
        
        