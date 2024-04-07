from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from accounts import models
from django.urls import reverse

class StudentAccountSerializer(ModelSerializer):
    session = serializers.StringRelatedField()
    
    class Meta:
        model = models.StudentAccount
        exclude = ['user']


class PendingStudentSerializer(ModelSerializer):
    session = serializers.StringRelatedField()
    approve_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()
    
    class Meta:
        model = models.StudentAccount
        exclude = ['user']
        
    def get_approve_url(self, obj):
        return reverse('accounts:approve_studentac', args=(obj.registration,))
    def get_delete_url(self, obj):
        return reverse('accounts:delete_studentac', args=(obj.registration,))