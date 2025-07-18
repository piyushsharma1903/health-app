from django.contrib import admin
from .models import MedicalReport


# Register your models here.
@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'report_type', 'upload_date')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'