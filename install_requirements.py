import subprocess
import sys

def install_requirements():
    """Install required packages"""
    try:
        print("Installing Django and required packages...")
        
        # Install required packages
        packages = [
            'django==4.2.7',
            'djangorestframework==3.14.0',
            'django-cors-headers==4.3.1',
            'python-decouple==3.8',
            'Pillow==10.1.0',
            'qrcode[pil]==7.4.2',
            'psycopg2-binary==2.9.7',
            'djangofilters==23.3',
            'reportlab==4.0.4',
            'pandas==2.1.4',
            'openpyxl==3.1.2'
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        
        print("All packages installed successfully!")
        
        # Now run migrations
        print("Running migrations...")
        subprocess.check_call([sys.executable, 'manage.py', 'migrate'])
        
        # Create admin user
        print("Creating admin user...")
        subprocess.check_call([sys.executable, 'create_admin_simple.py'])
        
        print("Setup completed successfully!")
        print("\nAdmin Credentials:")
        print("Username: msu-sndrotc_admin")
        print("Password: MSUSNDROTCU@2026")
        print("\nStarting development server...")
        subprocess.check_call([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])
        
    except Exception as e:
        print(f"Error during setup: {e}")

if __name__ == '__main__':
    install_requirements()
