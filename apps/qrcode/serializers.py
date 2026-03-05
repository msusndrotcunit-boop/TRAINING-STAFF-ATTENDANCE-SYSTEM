from rest_framework import serializers
from .models import QRCodeTemplate, QRCodeLog, QRCodeScanAttempt
from apps.attendance.models import AttendanceQRCode


class QRCodeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCodeTemplate
        fields = [
            'id', 'name', 'description', 'logo', 'background_color', 'foreground_color',
            'box_size', 'border', 'error_correction', 'is_default', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceQRCodeSerializer(serializers.ModelSerializer):
    session_title = serializers.CharField(source='session.title', read_only=True)
    session_date = serializers.DateField(source='session.date', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    scans_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = AttendanceQRCode
        fields = [
            'id', 'session', 'session_title', 'session_date', 'qr_code_data',
            'qr_code_image', 'is_active', 'expires_at', 'max_scans', 'scan_count',
            'created_by', 'created_by_name', 'created_at', 'is_expired', 'scans_remaining'
        ]
        read_only_fields = ['id', 'created_at', 'scan_count']


class QRCodeLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = QRCodeLog
        fields = [
            'id', 'qr_code', 'action', 'user', 'user_name', 'ip_address',
            'user_agent', 'location_data', 'timestamp', 'notes'
        ]
        read_only_fields = ['id', 'timestamp']


class QRCodeScanAttemptSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)
    
    class Meta:
        model = QRCodeScanAttempt
        fields = [
            'id', 'qr_code_data', 'staff', 'staff_name', 'status', 'ip_address',
            'user_agent', 'location_data', 'timestamp', 'error_message'
        ]
        read_only_fields = ['id', 'timestamp']
