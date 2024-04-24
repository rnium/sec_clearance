from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from accounts import models
from django.urls import reverse
from clearance.utils import get_admin_roles

class AdminAccountSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    # user_type = serializers.SerializerMethodField()
    class Meta:
        model = models.AdminAccount
        exclude = ['user', 'is_super_admin', 'invited_by', 'dept', 'profile_picture']
    
    def get_name(self, obj):
        return obj.full_name
    
    def get_email(self, obj):
        return obj.user.email
    
    def get_user_type(self, obj):
        return obj.get_user_type_display()
    
    def get_avatar_url(self, obj):
        return obj.avatar_url
    
    def get_roles(self, obj):
        the_roles = get_admin_roles(obj)
        for r in the_roles:
            r['code'] = ' '.join([fragment.upper() for fragment in r['code'].split('_')])
        return the_roles


class AdminAccountBasicSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    class Meta:
        model = models.AdminAccount
        exclude = ['user', 'is_super_admin', 'invited_by', 'dept', 'profile_picture']
    
    def get_name(self, obj):
        return obj.full_name
    
    def get_email(self, obj):
        return obj.user.email
    
    def get_department(self, obj):
        if dept:=obj.user.adminaccount.dept:
            return dept.display_name
        return "<Undesignated>"
    
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


class StudentProfileSerializer(ModelSerializer):
    session = serializers.StringRelatedField()
    hall = serializers.StringRelatedField()
    hall_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    class Meta:
        model = models.StudentAccount
        exclude = ['user', 'profile_picture']
        
    def get_name(self, obj):
        return obj.full_name
        
    def get_progress(self, obj):
        if hasattr(obj, 'clearance'):
            return obj.clearance.progress
        return 0

    def get_avatar_url(self, obj):
        return obj.avatar_url

    def get_hall_id(self, obj):
        if h:=obj.hall:
            return h.id
        return -1

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name


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
    hall = serializers.StringRelatedField()
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