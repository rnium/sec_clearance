from django.contrib import admin
from django.utils.html import format_html
from accounts import models

class PhotoDisplayMixin:
    def photo(self, obj):
        if obj.profile_picture:
            return format_html(f'<img src={obj.profile_picture.url} width="{70}" height="{70}" />')
        return "<No Photo>"


class StudentAdmin(admin.ModelAdmin, PhotoDisplayMixin):
    list_display = ('registration', 'session', 'photo', 'is_approved', 'hall')
    readonly_fields = ('registration', 'is_approved', 'session', 'hall', 'photo')
    empty_value_display = 'N/A'
    list_filter = ('is_approved', 'session')
    
    

class AdminAcAdmin(admin.ModelAdmin, PhotoDisplayMixin):
    list_display = ('name', 'photo', 'phone', 'dept', 'user_type', 'last_seen')
    list_filter = ('dept', 'user_type')
    ordering = ['-last_seen']
    
    @admin.display(description="Admin Name")
    def name(self, obj):
        return obj.full_name
    
    

admin.site.site_header = "Clearance Administration"
admin.site.site_title = "Backend"
admin.site.index_title = "Clearance Administration Backend"

admin.site.register(models.InviteToken)
admin.site.register(models.AdminAccount, AdminAcAdmin)
admin.site.register(models.StudentAccount, StudentAdmin)
admin.site.register(models.StudentPlaceholder)
admin.site.register(models.StudentNotice)
