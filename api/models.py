from django.db import models
from django.contrib.auth.models import User

class MedicalReport(models.Model):
    REPORT_CHOICES = [
        ('lab', 'Lab Report'),
        ('ct', 'CT Scan'),
        ('mri', 'MRI'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=10, choices=REPORT_CHOICES)
    upload_date = models.DateTimeField(auto_now_add=True)
    # Remove duplicate field - keep only one
    original_file = models.FileField(upload_to='reports/', blank=True, null=True)
    supabase_url = models.URLField(max_length=500, blank=True, null=True)  # For Supabase public URL
    extracted_data = models.JSONField(null=True, blank=True)
    ai_summary = models.TextField(null=True, blank=True)
    ai_prompt_preview = models.TextField(blank=True, null=True)
    report_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.report_type} - {self.upload_date}"