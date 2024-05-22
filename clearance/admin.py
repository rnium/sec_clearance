from django.contrib import admin
from clearance import models

class ClearanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'is_approved', 'progress', 'added_at')
    list_filter = ('is_approved', 'progress', 'added_at')
    list_per_page = 20
    readonly_fields = ('is_approved', 'progress', 'student')
    actions_on_top = False
    date_hierarchy = 'added_at'

admin.site.register(models.Department)
admin.site.register(models.Lab)
admin.site.register(models.Session)
admin.site.register(models.Clearance, ClearanceAdmin)
admin.site.register(models.AdministrativeApproval)
admin.site.register(models.DeptApproval)
admin.site.register(models.ClerkApproval)
admin.site.register(models.LabApproval)
