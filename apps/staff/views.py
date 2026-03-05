import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import TrainingStaff, StaffQualification, StaffPerformance, StaffSchedule
from .serializers import (
    TrainingStaffSerializer, StaffQualificationSerializer, 
    StaffPerformanceSerializer, StaffScheduleSerializer
)


class TrainingStaffViewSet(viewsets.ModelViewSet):
    queryset = TrainingStaff.objects.all()
    serializer_class = TrainingStaffSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'status']
    search_fields = ['user__full_name', 'user__service_number', 'user__email']
    ordering_fields = ['created_at', 'user__full_name']
    ordering = ['-created_at']


class StaffQualificationViewSet(viewsets.ModelViewSet):
    queryset = StaffQualification.objects.all()
    serializer_class = StaffQualificationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['staff', 'is_active']
    search_fields = ['qualification_name', 'issuing_authority']
    ordering_fields = ['date_obtained', 'qualification_name']
    ordering = ['-date_obtained']


class StaffPerformanceViewSet(viewsets.ModelViewSet):
    queryset = StaffPerformance.objects.all()
    serializer_class = StaffPerformanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['staff', 'evaluation_period']
    search_fields = ['staff__user__full_name', 'evaluation_period', 'remarks']
    ordering_fields = ['evaluation_date', 'overall_rating']
    ordering = ['-evaluation_date']


class StaffScheduleViewSet(viewsets.ModelViewSet):
    queryset = StaffSchedule.objects.all()
    serializer_class = StaffScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['staff', 'shift', 'date']
    search_fields = ['staff__user__full_name', 'duty_location', 'notes']
    ordering_fields = ['date', 'start_time']
    ordering = ['-date']


@login_required
def staff_list(request):
    """Staff listing page"""
    staff_list = TrainingStaff.objects.select_related('user').all()
    
    context = {
        'staff_list': staff_list,
    }
    return render(request, 'staff/list.html', context)


@login_required
def staff_detail(request, staff_id):
    """Staff detail page"""
    staff = get_object_or_404(TrainingStaff, id=staff_id)
    qualifications = staff.qualifications.filter(is_active=True)
    performance_records = staff.performance_records.all()
    schedules = staff.schedules.filter(date__gte=timezone.now().date()).order_by('date')
    
    context = {
        'staff': staff,
        'qualifications': qualifications,
        'performance_records': performance_records,
        'schedules': schedules,
    }
    return render(request, 'staff/detail.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_stats(request):
    """Get staff statistics"""
    total_staff = TrainingStaff.objects.count()
    active_staff = TrainingStaff.objects.filter(status='active').count()
    on_leave_staff = TrainingStaff.objects.filter(status='on_leave').count()
    
    # Staff by specialization
    specialization_stats = {}
    for specialization, label in TrainingStaff.SPECIALIZATION_CHOICES:
        count = TrainingStaff.objects.filter(specialization=specialization).count()
        specialization_stats[label] = count
    
    # Staff by rank
    from apps.authentication.models import User as AuthUser
    rank_stats = {}
    for rank, label in AuthUser.RANK_CHOICES:
        count = TrainingStaff.objects.filter(user__rank=rank).count()
        rank_stats[label] = count
    
    return Response({
        'total_staff': total_staff,
        'active_staff': active_staff,
        'on_leave_staff': on_leave_staff,
        'specialization_stats': specialization_stats,
        'rank_stats': rank_stats,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_staff_profile(request):
    """Create staff profile for existing user"""
    user_id = request.data.get('user_id')
    specialization = request.data.get('specialization')
    date_assigned = request.data.get('date_assigned')
    
    try:
        from apps.authentication.models import User
        user = User.objects.get(id=user_id)
        
        # Check if staff profile already exists
        if hasattr(user, 'staff_profile'):
            return Response({
                'success': False,
                'error': 'Staff profile already exists for this user'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create staff profile
        staff = TrainingStaff.objects.create(
            user=user,
            specialization=specialization,
            date_assigned=date_assigned,
        )
        
        serializer = TrainingStaffSerializer(staff)
        return Response({
            'success': True,
            'staff': serializer.data
        })
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error creating staff profile')
        return Response({
            'success': False,
            'error': 'An error occurred while creating staff profile. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_staff_status(request, staff_id):
    """Update staff status"""
    try:
        staff = TrainingStaff.objects.get(id=staff_id)
        new_status = request.data.get('status')
        
        if new_status not in dict(TrainingStaff.STATUS_CHOICES):
            return Response({
                'success': False,
                'error': 'Invalid status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        staff.status = new_status
        staff.save()
        
        serializer = TrainingStaffSerializer(staff)
        return Response({
            'success': True,
            'staff': serializer.data
        })
        
    except TrainingStaff.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Staff not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_schedule(request, staff_id=None):
    """Get staff schedule"""
    if staff_id:
        schedules = StaffSchedule.objects.filter(staff_id=staff_id)
    else:
        schedules = StaffSchedule.objects.all()
    
    # Filter by date range if provided
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if start_date:
        schedules = schedules.filter(date__gte=start_date)
    if end_date:
        schedules = schedules.filter(date__lte=end_date)
    
    serializer = StaffScheduleSerializer(schedules, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_schedule(request):
    """Create staff schedule"""
    try:
        data = request.data.copy()
        data['assigned_by'] = request.user.id
        
        serializer = StaffScheduleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'schedule': serializer.data
            })
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error updating staff status')
        return Response({
            'success': False,
            'error': 'An error occurred while updating staff status. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
