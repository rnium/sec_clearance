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


class ProgressiveStudentInfoSerializer(ModelSerializer):
    session = serializers.StringRelatedField()
    state = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = models.StudentAccount
        exclude = ['user', 'profile_picture']
    
    def get_state(self, obj):
        return obj.account_state
    
    def get_email(self, obj):
        return obj.user.email
    
    def get_first_name(self, obj):
        return obj.user.first_name
    
    def get_last_name(self, obj):
        return obj.user.last_name
    
    def get_avatar_url(self, obj):
        return obj.avatar_url