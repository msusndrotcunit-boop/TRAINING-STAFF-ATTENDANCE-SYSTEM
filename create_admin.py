#!/usr/bin/env python
import os
import django

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

if __name__ == '__main__':
    create_admin_user()
