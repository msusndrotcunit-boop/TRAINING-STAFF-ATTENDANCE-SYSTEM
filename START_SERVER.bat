@echo off
echo Starting MSU-SND ROTC Attendance System Setup...
echo.

echo Step 1: Running database migrations...
py manage.py migrate
if %errorlevel% neq 0 (
    echo Migration failed! Check error messages above.
    pause
    exit /b 1
)

echo.
echo Step 2: Creating admin user...
py manage.py shell -c "
from apps.authentication.models import User
try:
    admin = User.objects.get(email='msu-sndrotc_admin')
    print('Admin user already exists')
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
"

echo.
echo Step 3: Starting Django development server...
echo.
echo ========================================
echo MSU-SND ROTC Attendance System
echo ========================================
echo.
echo Admin Credentials:
echo Username: msu-sndrotc_admin
echo Password: MSUSNDROTCU@2026
echo.
echo Access URLs:
echo Landing Page: http://localhost:8000/
echo Admin Login:  http://localhost:8000/auth/admin/login/
echo Staff Login:  http://localhost:8000/auth/staff/login/
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

py manage.py runserver 0.0.0.0:8000
