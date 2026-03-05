from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Report(models.Model):
    TYPE_CHOICES = [
        ('attendance', 'Attendance Report'),
        ('performance', 'Performance Report'),
        ('staff_summary', 'Staff Summary Report'),
        ('training_summary', 'Training Summary Report'),
        ('qr_analytics', 'QR Code Analytics Report'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('scheduled', 'Scheduled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    description = models.TextField(blank=True, null=True)
    parameters = models.JSONField(default=dict, blank=True)  # Report parameters
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='generating')
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)  # in bytes
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    generated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class ReportSchedule(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=Report.TYPE_CHOICES)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    title_template = models.CharField(max_length=200)  # Template for report titles
    parameters = models.JSONField(default=dict, blank=True)
    recipients = models.ManyToManyField(User, related_name='scheduled_reports')
    is_active = models.BooleanField(default=True)
    next_run = models.DateTimeField()
    last_run = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_schedules'
        verbose_name = 'Report Schedule'
        verbose_name_plural = 'Report Schedules'
        ordering = ['next_run']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.get_frequency_display()}"


class ReportAccessLog(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20)  # 'viewed', 'downloaded', 'shared'
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_access_logs'
        verbose_name = 'Report Access Log'
        verbose_name_plural = 'Report Access Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        user_name = self.user.full_name if self.user else 'Anonymous'
        return f"{user_name} - {self.action} at {self.timestamp}"
