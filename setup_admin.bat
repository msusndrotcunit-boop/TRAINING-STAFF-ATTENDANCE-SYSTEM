@echo off
echo Creating admin user...
py create_admin.py
echo.
echo Admin user creation completed!
echo.
echo Username: msu-sndrotc_admin
echo Password: MSUSNDROTCU@2026
echo.
echo Starting Django development server...
py manage.py runserver
pause
