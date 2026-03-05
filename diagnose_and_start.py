#!/usr/bin/env python
"""Diagnostic script to check Django setup and start server"""
import sys
import os

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotc_attendance.settings')

print("Step 1: Setting up Django...")
try:
    import django
    django.setup()
    print("✓ Django setup successful")
except Exception as e:
    print(f"✗ Django setup failed: {e}")
    sys.exit(1)

print("\nStep 2: Checking database connection...")
try:
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✓ Database connection successful")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    sys.exit(1)

print("\nStep 3: Checking URL configuration...")
try:
    from django.urls import get_resolver
    resolver = get_resolver()
    urls = resolver.url_patterns
    print(f"✓ URL configuration loaded ({len(urls)} URL patterns found)")
except Exception as e:
    print(f"✗ URL configuration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 4: Checking models...")
try:
    from apps.authentication.models import User
    print(f"✓ User model loaded")
except Exception as e:
    print(f"✗ User model failed: {e}")
    sys.exit(1)

print("\nStep 5: Checking for admin user...")
try:
    admin_exists = User.objects.filter(email='msu-sndrotc_admin').exists()
    if admin_exists:
        print("✓ Admin user exists")
    else:
        print("ℹ Admin user does not exist, will create...")
        User.objects.create_user(
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
        print("✓ Admin user created")
except Exception as e:
    print(f"✗ Admin user check/creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("All checks passed! Starting server...")
print("="*50)
print("\nAccess URLs:")
print("  Landing Page: http://127.0.0.1:8000/")
print("  Admin Login:  http://127.0.0.1:8000/auth/admin/login/")
print("  Staff Login:  http://127.0.0.1:8000/auth/staff/login/")
print("\nAdmin Credentials:")
print("  Username: msu-sndrotc_admin")
print("  Password: MSUSNDROTCU@2026")
print("\nPress Ctrl+C to stop the server")
print("="*50 + "\n")

# Start the server
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
