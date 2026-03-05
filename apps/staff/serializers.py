from rest_framework import serializers
from .models import TrainingStaff, StaffQualification, StaffPerformance, StaffSchedule


class TrainingStaffSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_service_number = serializers.CharField(source='user.service_number', read_only=True)
    user_rank = serializers.CharField(source='user.get_rank_display', read_only=True)
    user_role = serializers.CharField(source='user.get_role_display', read_only=True)
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TrainingStaff
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_service_number',
            'user_rank', 'user_role', 'specialization', 'specialization_display',
            'status', 'status_display', 'date_assigned', 'bio', 'emergency_contact_name',
            'emergency_contact_number', 'blood_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StaffQualificationSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.full_name', read_only=True)
    
    class Meta:
        model = StaffQualification
        fields = [
            'id', 'staff', 'staff_name', 'qualification_name', 'issuing_authority',
            'certificate_number', 'date_obtained', 'expiry_date', 'certificate_file',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StaffPerformanceSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.full_name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.full_name', read_only=True)
    
    class Meta:
        model = StaffPerformance
        fields = [
            'id', 'staff', 'staff_name', 'evaluation_period', 'overall_rating',
            'leadership_rating', 'technical_skills_rating', 'discipline_rating',
            'evaluator', 'evaluator_name', 'remarks', 'evaluation_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StaffScheduleSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.full_name', read_only=True)
    shift_display = serializers.CharField(source='get_shift_display', read_only=True)
    
    class Meta:
        model = StaffSchedule
        fields = [
            'id', 'staff', 'staff_name', 'date', 'shift', 'shift_display',
            'duty_location', 'assigned_by', 'assigned_by_name', 'notes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
