from django.contrib import admin
from django.utils.html import format_html
from accounts import models

class StudentAdmin(admin.ModelAdmin):
    list_display = ('registration', 'session', 'photo', 'is_approved', 'hall')
    readonly_fields = ('registration', 'is_approved', 'session', 'hall', 'photo')
    empty_value_display = 'N/A'
    list_filter = ('is_approved', 'session')
    @admin.display(description="Photo")
    def photo(self, obj):
        return format_html(f'<img src={obj.profile_picture.url} width="{70}" height="{70}" />')

admin.site.site_header = "Clearance Administration"
admin.site.site_title = "Backend"
admin.site.index_title = "Clearance Administration"

admin.site.register(models.InviteToken)
admin.site.register(models.AdminAccount)
admin.site.register(models.StudentAccount, StudentAdmin)
admin.site.register(models.StudentPlaceholder)
admin.site.register(models.StudentNotice)
