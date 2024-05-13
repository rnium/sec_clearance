from django.contrib import admin
from accounts import models


admin.site.register(models.InviteToken)
admin.site.register(models.AdminAccount)
admin.site.register(models.StudentAccount)
admin.site.register(models.StudentPlaceholder)
admin.site.register(models.StudentNotice)
