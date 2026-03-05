from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('commander', 'Commander'),
        ('training_officer', 'Training Officer'),
        ('staff', 'Training Staff'),
        ('cadet', 'Cadet'),
    ]
    
    RANK_CHOICES = [
        ('col', 'Colonel'),
        ('ltc', 'Lieutenant Colonel'),
        ('maj', 'Major'),
        ('cpt', 'Captain'),
        ('1lt', 'First Lieutenant'),
        ('2lt', 'Second Lieutenant'),
        ('csm', 'Command Sergeant Major'),
        ('sgm', 'Sergeant Major'),
        ('msg', 'Master Sergeant'),
        ('ssg', 'Staff Sergeant'),
        ('sgt', 'Sergeant'),
        ('cpl', 'Corporal'),
        ('pfc', 'Private First Class'),
        ('pvt', 'Private'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    service_number = models.CharField(max_length=20, unique=True, help_text="Military service number")
    full_name = models.CharField(max_length=100)
    rank = models.CharField(max_length=10, choices=RANK_CHOICES)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'service_number', 'rank']
    
    class Meta:
        db_table = 'auth_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_rank_display()} {self.full_name} ({self.service_number})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_commander(self):
        return self.role == 'commander'
    
    @property
    def is_training_officer(self):
        return self.role == 'training_officer'
    
    @property
    def is_staff_user(self):
        return self.role == 'staff'
    
    @property
    def is_cadet(self):
        return self.role == 'cadet'


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.ip_address}"
