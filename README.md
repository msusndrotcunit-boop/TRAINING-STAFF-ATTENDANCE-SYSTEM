# MSU-SND ROTC Attendance Management System

A comprehensive QR code-based attendance management system designed specifically for the Mindanao State University - Sulu ROTC Unit. This system streamlines attendance tracking for training staff using modern QR code technology with a military-themed interface.

## Features

### 🎯 Core Features
- **QR Code Attendance**: Modern QR code scanning for quick and accurate attendance tracking
- **Staff Management**: Comprehensive staff profile and performance management
- **Training Sessions**: Schedule and manage various types of training sessions
- **Real-time Analytics**: Dashboard with attendance statistics and insights
- **Multi-format Reports**: Generate reports in PDF, Excel, and CSV formats

### 🔐 Security Features
- **Role-based Access Control**: Different access levels for administrators, commanders, and staff
- **QR Code Expiration**: Time-limited QR codes for enhanced security
- **Location Verification**: Optional GPS-based location verification
- **Audit Trail**: Complete logging of all attendance activities

### 📱 User Interface
- **Military Theme**: Professional army green military-themed design
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Intuitive Dashboard**: Easy-to-use interface for all user levels
- **Real-time Updates**: Live attendance status and notifications

## Technology Stack

### Backend
- **Framework**: Django 4.2.7
- **Database**: PostgreSQL
- **API**: Django REST Framework
- **Authentication**: Token-based authentication
- **QR Code**: qrcode library with PIL support

### Frontend
- **UI Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: jQuery 3.7.0
- **QR Scanner**: HTML5 QR Code Scanner

### Additional Libraries
- **PDF Generation**: ReportLab
- **Excel Export**: pandas with openpyxl
- **Image Processing**: Pillow
- **Security**: django-cors-headers, helmet

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Node.js (for frontend development, optional)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MSRTSAMS
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   - Copy `.env` file and configure your database settings
   - Update `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Usage

### For Administrators
1. Access the admin panel at `/admin/`
2. Create user accounts for training staff
3. Set up training sessions and schedules
4. Generate QR codes for attendance tracking
5. Monitor attendance through the dashboard

### For Training Staff
1. Log in with provided credentials
2. Use the QR scanner to mark attendance
3. View personal attendance history
4. Access training schedules

### For Commanders
1. Review attendance reports
2. Monitor staff performance
3. Generate analytical reports
4. Manage staff schedules

## Project Structure

```
MSRTSAMS/
├── apps/
│   ├── authentication/     # User authentication and profiles
│   ├── staff/             # Staff management
│   ├── attendance/        # Attendance tracking
│   ├── qrcode/           # QR code generation and scanning
│   └── reports/          # Report generation
├── templates/            # HTML templates
├── static/              # Static files (CSS, JS, images)
├── media/               # User uploads and generated files
├── rotc_attendance/     # Django project settings
├── requirements.txt     # Python dependencies
└── manage.py           # Django management script
```

## API Endpoints

### Authentication
- `POST /api/auth/api/login/` - User login
- `POST /api/auth/api/logout/` - User logout
- `GET /api/auth/api/profile/` - User profile

### Staff Management
- `GET /api/staff/api/staff/` - List staff
- `POST /api/staff/api/staff/` - Create staff
- `GET /api/staff/api/stats/` - Staff statistics

### Attendance
- `GET /api/attendance/api/sessions/` - List training sessions
- `POST /api/attendance/api/mark/` - Mark attendance
- `GET /api/attendance/api/stats/` - Attendance statistics

### QR Codes
- `POST /api/qrcode/api/generate/` - Generate QR code
- `POST /api/qrcode/api/scan/` - Scan QR code
- `GET /api/qrcode/api/list/` - List QR codes

### Reports
- `POST /api/reports/api/generate/attendance/` - Generate attendance report
- `GET /api/reports/api/download/<report_id>/` - Download report

## Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port

### QR Code Settings
- Default expiration: 60 minutes
- Maximum scans: 100 per QR code
- Supported formats: PNG
- Error correction: Medium

## Security Considerations

1. **QR Code Security**
   - Time-limited QR codes prevent unauthorized access
   - Unique identifiers prevent duplicate scanning
   - Location verification adds additional security layer

2. **Data Protection**
   - All sensitive data encrypted at rest
   - Secure authentication with token-based system
   - Audit trail for all attendance activities

3. **Access Control**
   - Role-based permissions
   - Session management
   - IP-based access logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For technical support or questions:
- Email: support@msu-snd-rotc.edu
- Documentation: Available in the `/docs/` directory
- Issues: Report via GitHub issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MSU-SND ROTC Unit for the requirements and testing
- Django community for the excellent framework
- Contributors who helped improve this system

---

**MSU-SND ROTC Attendance Management System** - Building Discipline Through Technology
