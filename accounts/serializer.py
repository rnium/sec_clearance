from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from accounts import models
from django.urls import reverse

class AdminAccountSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    # user_type = serializers.SerializerMethodField()
    class Meta:
        model = models.AdminAccount
        exclude = ['user', 'is_super_admin', 'invited_by', 'dept', 'profile_picture']
    
    def get_name(self, obj):
        return obj.full_name
    
    def get_user_type(self, obj):
        return obj.get_user_type_display()
    
    def get_avatar_url(self, obj):
        return obj.avatar_url

class StudentAccountSerializer(ModelSerializer):
    session = serializers.StringRelatedField()
    name = serializers.SerializerMethodField()
    class Meta:
        model = models.StudentAccount
        exclude = ['user']
        
    def get_name(self, obj):
        return obj.full_name


class PendingStudentSerializer(ModelSerializer):
    session = serializers.StringRelatedField()
    name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = models.StudentAccount
        exclude = ['user', 'profile_picture']
        
    def get_name(self, obj):
        return obj.full_name
    def get_avatar_url(self, obj):
        return obj.avatar_url


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