from django.contrib import admin
from clearance import models


admin.site.register(models.Department)
admin.site.register(models.Lab)
admin.site.register(models.Session)
admin.site.register(models.Clearance)
admin.site.register(models.AdministrativeApproval)
admin.site.register(models.DeptApproval)
admin.site.register(models.ClerkApproval)
admin.site.register(models.LabApproval)
