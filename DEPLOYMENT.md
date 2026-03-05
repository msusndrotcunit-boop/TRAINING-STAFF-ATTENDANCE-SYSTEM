# Deployment Guide

## Production Deployment

### Prerequisites
- Ubuntu 20.04+ or CentOS 8+
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Gunicorn
- SSL Certificate

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx curl -y

# Install project dependencies
sudo apt install libpq-dev python3-dev build-essential -y
```

### Step 2: Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE rotc_attendance;
CREATE USER rotc_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE rotc_attendance TO rotc_user;
\q
```

### Step 3: Application Setup

```bash
# Clone repository
git clone <your-repository-url> /var/www/rotc_attendance
cd /var/www/rotc_attendance

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
# Edit .env with production settings

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 4: Gunicorn Service

Create `/etc/systemd/system/rotc_attendance.service`:

```ini
[Unit]
Description=ROTC Attendance System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/rotc_attendance
Environment="PATH=/var/www/rotc_attendance/venv/bin"
EnvironmentFile=/var/www/rotc_attendance/.env
ExecStart=/var/www/rotc_attendance/venv/bin/gunicorn rotc_attendance.wsgi:application --workers 3 --bind unix:/var/www/rotc_attendance/rotc_attendance.sock

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl start rotc_attendance
sudo systemctl enable rotc_attendance
```

### Step 5: Nginx Configuration

Create `/etc/nginx/sites-available/rotc_attendance`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/rotc_attendance;
    }
    location /media/ {
        root /var/www/rotc_attendance;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/rotc_attendance/rotc_attendance.sock;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/rotc_attendance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Step 7: Security Hardening

```bash
# Configure firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable

# Set up log rotation
sudo nano /etc/logrotate.d/rotc_attendance
```

Content for log rotation:

```
/var/www/rotc_attendance/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload rotc_attendance
    endscript
}
```

### Step 8: Monitoring and Maintenance

```bash
# Set up monitoring scripts
sudo nano /usr/local/bin/rotc_backup.sh
```

Backup script content:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/rotc_attendance"
DB_NAME="rotc_attendance"
DB_USER="rotc_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /var/www/rotc_attendance/media/

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Make it executable and set up cron job:

```bash
sudo chmod +x /usr/local/bin/rotc_backup.sh
sudo crontab -e
```

Add to crontab:

```
0 2 * * * /usr/local/bin/rotc_backup.sh
```

## Environment Variables

Production `.env` file should contain:

```env
SECRET_KEY=your-very-secure-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DB_NAME=rotc_attendance
DB_USER=rotc_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_attendance_record_session ON attendance_attendancerecord(session_id);
CREATE INDEX idx_attendance_record_staff ON attendance_attendancerecord(staff_id);
CREATE INDEX idx_training_session_date ON attendance_trainingsession(date);
CREATE INDEX idx_qr_code_expires ON attendance_attendanceqrcode(expires_at);
```

### Caching

Add to Django settings:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Static File Optimization

```python
# In settings.py
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check if Gunicorn is running: `sudo systemctl status rotc_attendance`
   - Check logs: `sudo journalctl -u rotc_attendance`

2. **Database Connection Error**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check database credentials in `.env`

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic --noinput`
   - Check Nginx configuration for static file paths

4. **Permission Issues**
   - Ensure correct ownership: `sudo chown -R www-data:www-data /var/www/rotc_attendance`

### Log Locations

- Application logs: `/var/www/rotc_attendance/logs/`
- Nginx logs: `/var/log/nginx/`
- Gunicorn logs: `sudo journalctl -u rotc_attendance`

## Security Considerations

1. **Regular Updates**: Keep system and packages updated
2. **Firewall**: Configure UFW properly
3. **SSL**: Always use HTTPS in production
4. **Database**: Use strong passwords and limit access
5. **Backups**: Regular automated backups
6. **Monitoring**: Set up alerts for unusual activity

## Scaling

### Horizontal Scaling

- Use load balancer (HAProxy/Nginx)
- Multiple Gunicorn workers
- Database replication
- Redis for caching and sessions

### Vertical Scaling

- Increase server resources
- Optimize database queries
- Use CDN for static files
- Implement caching strategies
