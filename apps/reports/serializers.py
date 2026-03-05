from rest_framework import serializers
from .models import Report, ReportSchedule, ReportAccessLog


class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source='generated_by.full_name', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'report_type_display', 'format',
            'format_display', 'description', 'parameters', 'status', 'status_display',
            'file_path', 'file_size', 'generated_by', 'generated_by_name',
            'generated_at', 'expires_at', 'created_at', 'updated_at', 'is_expired'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'generated_at']


class ReportScheduleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    recipients_list = serializers.StringRelatedField(source='recipients', many=True, read_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'report_type', 'report_type_display', 'frequency',
            'frequency_display', 'title_template', 'parameters', 'recipients',
            'recipients_list', 'is_active', 'next_run', 'last_run',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_run']


class ReportAccessLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = ReportAccessLog
        fields = [
            'id', 'report', 'user', 'user_name', 'action', 'ip_address',
            'user_agent', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
