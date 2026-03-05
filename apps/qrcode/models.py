from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class QRCodeTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='qr_templates/logos/', blank=True, null=True)
    background_color = models.CharField(max_length=7, default='#FFFFFF')  # Hex color
    foreground_color = models.CharField(max_length=7, default='#000000')  # Hex color
    box_size = models.PositiveIntegerField(default=10)
    border = models.PositiveIntegerField(default=4)
    error_correction = models.CharField(
        max_length=1,
        choices=[
            ('L', 'Low'),
            ('M', 'Medium'),
            ('Q', 'Quartile'),
            ('H', 'High'),
        ],
        default='M'
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'qr_code_templates'
        verbose_name = 'QR Code Template'
        verbose_name_plural = 'QR Code Templates'
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return self.name


class QRCodeLog(models.Model):
    ACTION_CHOICES = [
        ('generated', 'Generated'),
        ('scanned', 'Scanned'),
        ('expired', 'Expired'),
        ('deactivated', 'Deactivated'),
        ('reactivated', 'Reactivated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ForeignKey('attendance.AttendanceQRCode', on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=15, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    location_data = models.JSONField(null=True, blank=True)  # GPS coordinates if available
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'qr_code_logs'
        verbose_name = 'QR Code Log'
        verbose_name_plural = 'QR Code Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.qr_code.session.title} - {self.action} at {self.timestamp}"


class QRCodeScanAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('expired', 'Expired QR Code'),
        ('invalid', 'Invalid QR Code'),
        ('duplicate', 'Duplicate Scan'),
        ('location_mismatch', 'Location Mismatch'),
        ('session_not_found', 'Session Not Found'),
        ('staff_not_registered', 'Staff Not Registered'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code_data = models.CharField(max_length=500)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    location_data = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'qr_code_scan_attempts'
        verbose_name = 'QR Code Scan Attempt'
        verbose_name_plural = 'QR Code Scan Attempts'
        ordering = ['-timestamp']
    
    def __str__(self):
        staff_name = self.staff.full_name if self.staff else 'Unknown'
        return f"{staff_name} - {self.status} at {self.timestamp}"
