from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class TrainingStaff(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('transferred', 'Transferred'),
        ('retired', 'Retired'),
    ]
    
    SPECIALIZATION_CHOICES = [
        ('infantry', 'Infantry'),
        ('artillery', 'Artillery'),
        ('engineering', 'Engineering'),
        ('signals', 'Signals'),
        ('medical', 'Medical'),
        ('logistics', 'Logistics'),
        ('admin', 'Administration'),
        ('drill', 'Drill & Ceremony'),
        ('marksmanship', 'Marksmanship'),
        ('physical_training', 'Physical Training'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    date_assigned = models.DateField()
    bio = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True, null=True)
    blood_type = models.CharField(max_length=5, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'training_staff'
        verbose_name = 'Training Staff'
        verbose_name_plural = 'Training Staff'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_specialization_display()}"


class StaffQualification(models.Model):
    staff = models.ForeignKey(TrainingStaff, on_delete=models.CASCADE, related_name='qualifications')
    qualification_name = models.CharField(max_length=100)
    issuing_authority = models.CharField(max_length=100)
    certificate_number = models.CharField(max_length=50, blank=True, null=True)
    date_obtained = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    certificate_file = models.FileField(upload_to='qualifications/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'staff_qualifications'
        verbose_name = 'Staff Qualification'
        verbose_name_plural = 'Staff Qualifications'
        ordering = ['-date_obtained']
    
    def __str__(self):
        return f"{self.staff.user.full_name} - {self.qualification_name}"


class StaffPerformance(models.Model):
    staff = models.ForeignKey(TrainingStaff, on_delete=models.CASCADE, related_name='performance_records')
    evaluation_period = models.CharField(max_length=50)  # e.g., "Q1 2024", "Annual 2023"
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2)  # e.g., 4.50
    leadership_rating = models.DecimalField(max_digits=3, decimal_places=2)
    technical_skills_rating = models.DecimalField(max_digits=3, decimal_places=2)
    discipline_rating = models.DecimalField(max_digits=3, decimal_places=2)
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='evaluations_given')
    remarks = models.TextField(blank=True, null=True)
    evaluation_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'staff_performance'
        verbose_name = 'Staff Performance'
        verbose_name_plural = 'Staff Performance Records'
        ordering = ['-evaluation_date']
        unique_together = ['staff', 'evaluation_period']
    
    def __str__(self):
        return f"{self.staff.user.full_name} - {self.evaluation_period}"


class StaffSchedule(models.Model):
    SHIFT_CHOICES = [
        ('morning', 'Morning (6:00-14:00)'),
        ('afternoon', 'Afternoon (14:00-22:00)'),
        ('night', 'Night (22:00-6:00)'),
        ('flexible', 'Flexible'),
    ]
    
    staff = models.ForeignKey(TrainingStaff, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    duty_location = models.CharField(max_length=100)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_schedules')
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff_schedules'
        verbose_name = 'Staff Schedule'
        verbose_name_plural = 'Staff Schedules'
        ordering = ['-date']
        unique_together = ['staff', 'date']
    
    def __str__(self):
        return f"{self.staff.user.full_name} - {self.date} ({self.get_shift_display()})"
