from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'rank', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'rank', 'is_active', 'created_at')
    search_fields = ('email', 'full_name', 'service_number')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'service_number', 'rank', 'contact_number', 'profile_picture')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'service_number', 'rank', 'role', 'password1', 'password2'),
        }),
    )
