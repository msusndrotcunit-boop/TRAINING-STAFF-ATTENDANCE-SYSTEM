from rest_framework import serializers
from .models import TrainingSession, AttendanceRecord, AttendanceQRCode, AttendanceSummary


class TrainingSessionSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    instructor_rank = serializers.CharField(source='instructor.get_rank_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    
    class Meta:
        model = TrainingSession
        fields = [
            'id', 'title', 'description', 'session_type', 'session_type_display',
            'date', 'start_time', 'end_time', 'duration_hours', 'location',
            'instructor', 'instructor_name', 'instructor_rank', 'status',
            'status_display', 'max_participants', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceRecordSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)
    staff_rank = serializers.CharField(source='staff.get_rank_display', read_only=True)
    session_title = serializers.CharField(source='session.title', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'session', 'session_title', 'staff', 'staff_name', 'staff_rank',
            'status', 'status_display', 'check_in_time', 'check_out_time',
            'qr_code_scanned', 'qr_code_scan_time', 'location_verified',
            'notes', 'marked_by', 'marked_by_name', 'created_at', 'updated_at'
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


class AttendanceSummarySerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    
    class Meta:
        model = AttendanceSummary
        fields = [
            'id', 'staff', 'staff_name', 'period', 'period_display',
            'start_date', 'end_date', 'total_sessions', 'present_count',
            'absent_count', 'late_count', 'excused_count', 'attendance_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
