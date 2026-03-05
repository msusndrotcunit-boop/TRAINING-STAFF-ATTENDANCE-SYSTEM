from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class TrainingSession(models.Model):
    TYPE_CHOICES = [
        ('drill', 'Drill & Ceremony'),
        ('classroom', 'Classroom Instruction'),
        ('field_training', 'Field Training'),
        ('physical_training', 'Physical Training'),
        ('marksmanship', 'Marksmanship Training'),
        ('first_aid', 'First Aid Training'),
        ('leadership', 'Leadership Development'),
        ('specialized', 'Specialized Training'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    session_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='instructed_sessions')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    max_participants = models.PositiveIntegerField(default=50)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'training_sessions'
        verbose_name = 'Training Session'
        verbose_name_plural = 'Training Sessions'
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    @property
    def duration_hours(self):
        from datetime import datetime, time
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        return (end - start).total_seconds() / 3600


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
        ('sick_leave', 'Sick Leave'),
        ('emergency_leave', 'Emergency Leave'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='attendance_records')
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='present')
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    qr_code_scanned = models.BooleanField(default=False)
    qr_code_scan_time = models.DateTimeField(null=True, blank=True)
    location_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance_records'
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        ordering = ['-created_at']
        unique_together = ['session', 'staff']
    
    def __str__(self):
        return f"{self.staff.full_name} - {self.session.title} ({self.status})"


class AttendanceQRCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='qr_codes')
    qr_code_data = models.CharField(max_length=500, unique=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    max_scans = models.PositiveIntegerField(default=100)
    scan_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_qr_codes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendance_qr_codes'
        verbose_name = 'Attendance QR Code'
        verbose_name_plural = 'Attendance QR Codes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"QR Code for {self.session.title}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def scans_remaining(self):
        return max(0, self.max_scans - self.scan_count)


class AttendanceSummary(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_summaries')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_sessions = models.PositiveIntegerField(default=0)
    present_count = models.PositiveIntegerField(default=0)
    absent_count = models.PositiveIntegerField(default=0)
    late_count = models.PositiveIntegerField(default=0)
    excused_count = models.PositiveIntegerField(default=0)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance_summaries'
        verbose_name = 'Attendance Summary'
        verbose_name_plural = 'Attendance Summaries'
        ordering = ['-end_date']
        unique_together = ['staff', 'period', 'start_date', 'end_date']
    
    def __str__(self):
        return f"{self.staff.full_name} - {self.period} Summary ({self.start_date} to {self.end_date})"
    
    def calculate_attendance_rate(self):
        if self.total_sessions > 0:
            self.attendance_rate = (self.present_count / self.total_sessions) * 100
        else:
            self.attendance_rate = 0.00
        self.save()
