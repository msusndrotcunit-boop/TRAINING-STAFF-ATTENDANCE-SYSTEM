# MSU-SND ROTC Attendance System - Setup Guide

## 🚀 Quick Start

This guide will help you set up the MSU-SND ROTC Attendance Management System with the new landing page and separate login portals.

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Node.js (optional, for development)
- Git

## 🛠️ Installation Steps

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd MSRTSAMS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE rotc_attendance;
CREATE USER rotc_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE rotc_attendance TO rotc_user;
\q
```

### 3. Environment Setup

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required environment variables:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=rotc_attendance
DB_USER=rotc_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Database Migration

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (administrator account)
python manage.py createsuperuser
```

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 6. Start Development Server

```bash
python manage.py runserver
```

## 🌐 Access Points

Once the server is running, you can access:

### Main Landing Page
- **URL**: `http://localhost:8000/`
- **Purpose**: Welcome page with system overview
- **Features**: 
  - System capabilities showcase
  - Login buttons for staff and admin
  - Interactive demo and statistics

### Staff Login Portal
- **URL**: `http://localhost:8000/auth/staff/login/`
- **Purpose**: Training staff and instructor login
- **Features**:
  - Military-themed staff interface
  - Account request functionality
  - System status display
  - Quick help links

### Administrator Login Portal
- **URL**: `http://localhost:8000/auth/admin/login/`
- **Purpose**: System administrator access
- **Features**:
  - Enhanced security interface
  - System monitoring tools
  - Administrative quick actions
  - Performance metrics

### Django Admin Panel
- **URL**: `http://localhost:8000/admin/`
- **Purpose**: Backend administration
- **Features**:
  - User management
  - Database administration
  - System configuration

## 👥 User Roles and Access

### Administrator
- **Login**: Admin portal
- **Access**: Full system control
- **Features**: User management, system settings, reports
- **Default Redirect**: `/admin/`

### Training Staff
- **Login**: Staff portal
- **Access**: Attendance marking, personal records
- **Features**: QR scanning, schedule view, performance tracking
- **Default Redirect**: `/dashboard/`

### Commanders & Officers
- **Login**: Staff portal
- **Access**: Enhanced staff features
- **Features**: Report generation, team management
- **Default Redirect**: `/dashboard/`

## 🔐 Default Login Credentials

After creating a superuser, you can use:
- **Email**: Your superuser email
- **Password**: Your superuser password
- **Access**: Administrator portal

## 📱 Mobile Access

The system is fully responsive:
- **Desktop**: Full functionality
- **Tablet**: Optimized interface
- **Mobile**: Core features available

## 🔧 Configuration Options

### Customizing Landing Page
Edit `templates/landing.html` to modify:
- Hero section content
- Feature descriptions
- Statistics
- Call-to-action buttons

### Customizing Login Pages
- **Staff**: `templates/authentication/staff_login.html`
- **Admin**: `templates/authentication/admin_login.html`

### Military Theme Customization
Edit `templates/base.html` CSS variables:
```css
:root {
    --army-green: #4B5320;
    --army-dark-green: #2E3A1F;
    --army-light-green: #6B7E3A;
    --army-tan: #C2B280;
    --army-gold: #FFD700;
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Verify database exists
   sudo -u postgres psql -l
   ```

2. **Static Files Not Loading**
   ```bash
   # Recollect static files
   python manage.py collectstatic --noinput --clear
   ```

3. **Login Redirect Issues**
   - Check URL configuration in `rotc_attendance/urls.py`
   - Verify authentication views are properly configured

4. **Permission Errors**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   chmod -R 755 .
   ```

### Debug Mode

Enable debug mode in `.env`:
```env
DEBUG=True
```

Check logs for detailed error information.

## 📊 Testing the System

### 1. Test Landing Page
- Visit `http://localhost:8000/`
- Verify all sections load correctly
- Test login buttons redirect properly

### 2. Test Staff Login
- Go to staff login portal
- Try login with valid credentials
- Verify dashboard redirect

### 3. Test Admin Login
- Go to admin login portal
- Try login with admin credentials
- Verify admin panel access

### 4. Test QR Code Features
- Access QR code generator
- Test QR code scanning
- Verify attendance marking

## 🔒 Security Considerations

1. **Change Default Passwords**: Immediately after setup
2. **Use HTTPS**: In production environments
3. **Regular Updates**: Keep dependencies updated
4. **Access Control**: Limit admin access
5. **Backup**: Regular database backups

## 📞 Support

For technical support:
- Check the documentation in `README.md`
- Review deployment guide in `DEPLOYMENT.md`
- Contact system administrator

## 🎯 Next Steps

After successful setup:

1. **Create User Accounts**: Add staff and administrators
2. **Configure Training Sessions**: Set up training schedules
3. **Test QR Code System**: Generate and scan test codes
4. **Generate Reports**: Test report functionality
5. **Train Users**: Provide training to staff members

---

**MSU-SND ROTC Attendance Management System** - Ready for deployment! 🎉
