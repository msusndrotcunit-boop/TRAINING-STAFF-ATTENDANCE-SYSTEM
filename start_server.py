#!/usr/bin/env python
import os
import django
from django.core.management import execute_from_command_line

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotc_attendance.settings')

# Setup Django
django.setup()

from apps.authentication.models import User

def create_admin_user():
    """Create admin user if it doesn't exist"""
    try:
        admin = User.objects.get(email='msu-sndrotc_admin')
        print('Admin user already exists')
        return admin
    except User.DoesNotExist:
        admin = User.objects.create_user(
            email='msu-sndrotc_admin',
            password='MSUSNDROTCU@2026',
            first_name='MSU-SND',
            last_name='ROTC Administrator',
            full_name='MSU-SND ROTC Administrator',
            rank='COL',
            role='admin',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        print('Admin user created successfully')
        return admin

def run_migrations():
    """Run database migrations"""
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print('Migrations completed successfully')
    except Exception as e:
        print(f'Migration error: {e}')

def run_server():
    """Start Django development server"""
    try:
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
    except Exception as e:
        print(f'Server error: {e}')

if __name__ == '__main__':
    print("Setting up MSU-SND ROTC Attendance System...")
    
    # Create admin user
    create_admin_user()
    
    # Run migrations
    run_migrations()
    
    # Start server
    print("\nStarting Django development server...")
    print("Admin Credentials:")
    print("Username: msu-sndrotc_admin")
    print("Password: MSUSNDROTCU@2026")
    print("\nAccess the system at: http://localhost:8000")
    print("Landing page: http://localhost:8000/")
    print("Admin login: http://localhost:8000/auth/admin/login/")
    print("Staff login: http://localhost:8000/auth/staff/login/")
    
    run_server()
