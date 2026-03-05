import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
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
from datetime import datetime, timedelta
from .models import TrainingSession, AttendanceRecord, AttendanceQRCode, AttendanceSummary
from .serializers import (
    TrainingSessionSerializer, AttendanceRecordSerializer,
    AttendanceQRCodeSerializer, AttendanceSummarySerializer
)


class TrainingSessionViewSet(viewsets.ModelViewSet):
    queryset = TrainingSession.objects.all()
    serializer_class = TrainingSessionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['session_type', 'status', 'date']
    search_fields = ['title', 'description', 'location', 'instructor__full_name']
    ordering_fields = ['date', 'start_time', 'title']
    ordering = ['-date', '-start_time']


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['session', 'staff', 'status', 'check_in_time']
    search_fields = ['staff__full_name', 'session__title', 'notes']
    ordering_fields = ['check_in_time', 'created_at']
    ordering = ['-check_in_time']


class AttendanceQRCodeViewSet(viewsets.ModelViewSet):
    queryset = AttendanceQRCode.objects.all()
    serializer_class = AttendanceQRCodeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['session', 'is_active']
    search_fields = ['session__title']
    ordering_fields = ['created_at', 'expires_at']
    ordering = ['-created_at']


class AttendanceSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttendanceSummary.objects.all()
    serializer_class = AttendanceSummarySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['staff', 'period', 'start_date', 'end_date']
    search_fields = ['staff__full_name']
    ordering_fields = ['end_date', 'attendance_rate']
    ordering = ['-end_date']


@login_required
def attendance_dashboard(request):
    """Attendance dashboard page"""
    today = timezone.now().date()
    
    # Get today's sessions
    today_sessions = TrainingSession.objects.filter(date=today).order_by('start_time')
    
    # Get recent attendance records
    recent_attendance = AttendanceRecord.objects.select_related('staff', 'session').order_by('-check_in_time')[:10]
    
    # Get attendance statistics
    total_records = AttendanceRecord.objects.filter(session__date=today).count()
    present_records = AttendanceRecord.objects.filter(session__date=today, status='present').count()
    
    context = {
        'today_sessions': today_sessions,
        'recent_attendance': recent_attendance,
        'total_records': total_records,
        'present_records': present_records,
        'attendance_rate': (present_records / total_records * 100) if total_records > 0 else 0,
    }
    return render(request, 'attendance/dashboard.html', context)


@login_required
def session_attendance(request, session_id):
    """Session attendance detail page"""
    session = get_object_or_404(TrainingSession, id=session_id)
    attendance_records = AttendanceRecord.objects.filter(session=session).select_related('staff')
    
    context = {
        'session': session,
        'attendance_records': attendance_records,
    }
    return render(request, 'attendance/session_detail.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_stats(request):
    """Get attendance statistics"""
    # Date range from query params
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
    
    # Get statistics
    total_sessions = TrainingSession.objects.filter(date__range=[start_date, end_date]).count()
    total_attendance = AttendanceRecord.objects.filter(session__date__range=[start_date, end_date]).count()
    present_attendance = AttendanceRecord.objects.filter(
        session__date__range=[start_date, end_date],
        status='present'
    ).count()
    absent_attendance = AttendanceRecord.objects.filter(
        session__date__range=[start_date, end_date],
        status='absent'
    ).count()
    late_attendance = AttendanceRecord.objects.filter(
        session__date__range=[start_date, end_date],
        status='late'
    ).count()
    
    # Daily attendance trend
    daily_stats = []
    current_date = start_date
    while current_date <= end_date:
        day_total = AttendanceRecord.objects.filter(session__date=current_date).count()
        day_present = AttendanceRecord.objects.filter(session__date=current_date, status='present').count()
        day_rate = (day_present / day_total * 100) if day_total > 0 else 0
        
        daily_stats.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'total': day_total,
            'present': day_present,
            'rate': round(day_rate, 2)
        })
        current_date += timedelta(days=1)
    
    return Response({
        'total_sessions': total_sessions,
        'total_attendance': total_attendance,
        'present_attendance': present_attendance,
        'absent_attendance': absent_attendance,
        'late_attendance': late_attendance,
        'attendance_rate': round((present_attendance / total_attendance * 100) if total_attendance > 0 else 0, 2),
        'daily_stats': daily_stats,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    """Mark attendance manually"""
    session_id = request.data.get('session_id')
    staff_id = request.data.get('staff_id')
    attendance_status = request.data.get('status', 'present')
    notes = request.data.get('notes', '')
    
    try:
        session = TrainingSession.objects.get(id=session_id)
        from apps.authentication.models import User
        staff_user = User.objects.get(id=staff_id)
        
        # Check if attendance already exists
        existing_record = AttendanceRecord.objects.filter(
            session=session,
            staff=staff_user
        ).first()
        
        if existing_record:
            # Update existing record
            existing_record.status = attendance_status
            existing_record.notes = notes
            existing_record.marked_by = request.user
            existing_record.save()
            record = existing_record
        else:
            # Create new record
            record = AttendanceRecord.objects.create(
                session=session,
                staff=staff_user,
                status=attendance_status,
                check_in_time=timezone.now(),
                notes=notes,
                marked_by=request.user
            )
        
        serializer = AttendanceRecordSerializer(record)
        return Response({
            'success': True,
            'attendance': serializer.data
        })
        
    except (TrainingSession.DoesNotExist, User.DoesNotExist):
        return Response({
            'success': False,
            'error': 'Session or staff not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error marking attendance')
        return Response({
            'success': False,
            'error': 'An error occurred while marking attendance. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_mark_attendance(request):
    """Mark attendance for multiple staff"""
    session_id = request.data.get('session_id')
    attendance_data = request.data.get('attendance_data', [])  # List of {staff_id, status, notes}
    
    try:
        session = TrainingSession.objects.get(id=session_id)
        from apps.authentication.models import User
        
        results = []
        
        for data in attendance_data:
            staff_id = data.get('staff_id')
            status = data.get('status', 'present')
            notes = data.get('notes', '')
            
            try:
                staff_user = User.objects.get(id=staff_id)
                
                # Check if attendance already exists
                existing_record = AttendanceRecord.objects.filter(
                    session=session,
                    staff=staff_user
                ).first()
                
                if existing_record:
                    existing_record.status = status
                    existing_record.notes = notes
                    existing_record.marked_by = request.user
                    existing_record.save()
                    record = existing_record
                else:
                    record = AttendanceRecord.objects.create(
                        session=session,
                        staff=staff_user,
                        status=status,
                        check_in_time=timezone.now(),
                        notes=notes,
                        marked_by=request.user
                    )
                
                serializer = AttendanceRecordSerializer(record)
                results.append({
                    'success': True,
                    'staff_id': staff_id,
                    'attendance': serializer.data
                })
                
            except User.DoesNotExist:
                results.append({
                    'success': False,
                    'staff_id': staff_id,
                    'error': 'Staff not found'
                })
        
        return Response({
            'success': True,
            'results': results
        })
        
    except TrainingSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error in bulk attendance')
        return Response({
            'success': False,
            'error': 'An error occurred while processing bulk attendance. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_attendance_list(request, session_id):
    """Get attendance list for a specific session"""
    try:
        session = TrainingSession.objects.get(id=session_id)
        attendance_records = AttendanceRecord.objects.filter(session=session).select_related('staff')
        
        serializer = AttendanceRecordSerializer(attendance_records, many=True)
        return Response({
            'success': True,
            'session': TrainingSessionSerializer(session).data,
            'attendance': serializer.data
        })
        
    except TrainingSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_attendance_summary(request):
    """Generate attendance summary for a period"""
    staff_id = request.data.get('staff_id')
    period = request.data.get('period', 'monthly')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    
    try:
        from apps.authentication.models import User
        staff = User.objects.get(id=staff_id)
        
        # Parse dates
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Calculate attendance statistics
        attendance_records = AttendanceRecord.objects.filter(
            staff=staff,
            session__date__range=[start_date, end_date]
        )
        
        total_sessions = attendance_records.count()
        present_count = attendance_records.filter(status='present').count()
        absent_count = attendance_records.filter(status='absent').count()
        late_count = attendance_records.filter(status='late').count()
        excused_count = attendance_records.filter(status='excused').count()
        
        # Create or update summary
        summary, created = AttendanceSummary.objects.update_or_create(
            staff=staff,
            period=period,
            start_date=start_date,
            end_date=end_date,
            defaults={
                'total_sessions': total_sessions,
                'present_count': present_count,
                'absent_count': absent_count,
                'late_count': late_count,
                'excused_count': excused_count,
            }
        )
        
        summary.calculate_attendance_rate()
        
        serializer = AttendanceSummarySerializer(summary)
        return Response({
            'success': True,
            'summary': serializer.data
        })
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Staff not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error generating attendance summary')
        return Response({
            'success': False,
            'error': 'An error occurred while generating the attendance summary. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
