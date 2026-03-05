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
import csv
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import pandas as pd

from .models import Report, ReportSchedule, ReportAccessLog
from .serializers import ReportSerializer, ReportScheduleSerializer
from apps.attendance.models import AttendanceRecord, TrainingSession
from apps.staff.models import TrainingStaff


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'format', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'generated_at']
    ordering = ['-created_at']


class ReportScheduleViewSet(viewsets.ModelViewSet):
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'frequency', 'is_active']
    search_fields = ['title_template']
    ordering_fields = ['next_run', 'created_at']
    ordering = ['next_run']


@login_required
def reports_dashboard(request):
    """Reports dashboard page"""
    recent_reports = Report.objects.filter(generated_by=request.user).order_by('-created_at')[:10]
    active_schedules = ReportSchedule.objects.filter(is_active=True).order_by('next_run')
    
    context = {
        'recent_reports': recent_reports,
        'active_schedules': active_schedules,
    }
    return render(request, 'reports/dashboard.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_attendance_report(request):
    """Generate attendance report"""
    report_type = request.data.get('report_type', 'attendance')
    format_type = request.data.get('format', 'pdf')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    session_type = request.data.get('session_type', '')
    
    try:
        # Parse dates
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().date() - timedelta(days=30)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
        
        # Get attendance data
        queryset = AttendanceRecord.objects.filter(
            session__date__range=[start_date, end_date]
        ).select_related('staff', 'session')
        
        if session_type:
            queryset = queryset.filter(session__session_type=session_type)
        
        # Generate report based on format
        if format_type == 'pdf':
            file_path, file_size = generate_pdf_report(queryset, start_date, end_date, report_type)
        elif format_type == 'excel':
            file_path, file_size = generate_excel_report(queryset, start_date, end_date, report_type)
        elif format_type == 'csv':
            file_path, file_size = generate_csv_report(queryset, start_date, end_date, report_type)
        else:
            return Response({
                'success': False,
                'error': 'Unsupported format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create report record
        report = Report.objects.create(
            title=f"{report_type.title()} Report - {start_date} to {end_date}",
            report_type=report_type,
            format=format_type,
            parameters={
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'session_type': session_type
            },
            status='completed',
            file_path=file_path,
            file_size=file_size,
            generated_by=request.user,
            generated_at=timezone.now()
        )
        
        serializer = ReportSerializer(report)
        return Response({
            'success': True,
            'report': serializer.data
        })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error generating attendance report')
        return Response({
            'success': False,
            'error': 'An error occurred while generating the report. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_staff_performance_report(request):
    """Generate staff performance report"""
    format_type = request.data.get('format', 'pdf')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    specialization = request.data.get('specialization', '')
    
    try:
        # Parse dates
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().date() - timedelta(days=90)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
        
        # Get staff performance data
        queryset = TrainingStaff.objects.all().select_related('user')
        
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        
        # Generate report
        if format_type == 'pdf':
            file_path, file_size = generate_staff_pdf_report(queryset, start_date, end_date)
        elif format_type == 'excel':
            file_path, file_size = generate_staff_excel_report(queryset, start_date, end_date)
        else:
            return Response({
                'success': False,
                'error': 'Unsupported format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create report record
        report = Report.objects.create(
            title=f"Staff Performance Report - {start_date} to {end_date}",
            report_type='performance',
            format=format_type,
            parameters={
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'specialization': specialization
            },
            status='completed',
            file_path=file_path,
            file_size=file_size,
            generated_by=request.user,
            generated_at=timezone.now()
        )
        
        serializer = ReportSerializer(report)
        return Response({
            'success': True,
            'report': serializer.data
        })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error generating staff performance report')
        return Response({
            'success': False,
            'error': 'An error occurred while generating the report. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report(request, report_id):
    """Download generated report"""
    try:
        report = get_object_or_404(Report, id=report_id)
        
        # Log access
        ReportAccessLog.objects.create(
            report=report,
            user=request.user,
            action='downloaded',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Serve file
        if report.file_path:
            try:
                with open(report.file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename="{report.title}.{report.format}"'
                    response['Content-Length'] = report.file_size or 0
                    return response
            except FileNotFoundError:
                return Response({
                    'success': False,
                    'error': 'Report file not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False,
                'error': 'No file available for this report'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error downloading report')
        return Response({
            'success': False,
            'error': 'An error occurred while downloading the report. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_pdf_report(queryset, start_date, end_date, report_type):
    """Generate PDF report"""
    from django.conf import settings
    import os
    
    # Create filename
    filename = f"attendance_report_{start_date}_{end_date}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create PDF
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    story.append(Paragraph("MSU-SND ROTC Attendance Report", title_style))
    story.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Create table data
    data = [['Staff Name', 'Rank', 'Session', 'Date', 'Status', 'Check In Time']]
    
    for record in queryset:
        data.append([
            record.staff.full_name,
            record.staff.get_rank_display(),
            record.session.title,
            record.session.date.strftime('%Y-%m-%d'),
            record.get_status_display(),
            record.check_in_time.strftime('%H:%M') if record.check_in_time else 'N/A'
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    doc.build(story)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    return file_path, file_size


def generate_excel_report(queryset, start_date, end_date, report_type):
    """Generate Excel report"""
    from django.conf import settings
    import os
    
    # Create filename
    filename = f"attendance_report_{start_date}_{end_date}.xlsx"
    file_path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create DataFrame
    data = []
    for record in queryset:
        data.append({
            'Staff Name': record.staff.full_name,
            'Rank': record.staff.get_rank_display(),
            'Session': record.session.title,
            'Date': record.session.date.strftime('%Y-%m-%d'),
            'Status': record.get_status_display(),
            'Check In Time': record.check_in_time.strftime('%H:%M') if record.check_in_time else 'N/A',
            'QR Code Scanned': 'Yes' if record.qr_code_scanned else 'No',
            'Location Verified': 'Yes' if record.location_verified else 'No'
        })
    
    df = pd.DataFrame(data)
    
    # Save to Excel
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Attendance Report', index=False)
        
        # Get worksheet for formatting
        worksheet = writer.sheets['Attendance Report']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    return file_path, file_size


def generate_csv_report(queryset, start_date, end_date, report_type):
    """Generate CSV report"""
    from django.conf import settings
    import os
    
    # Create filename
    filename = f"attendance_report_{start_date}_{end_date}.csv"
    file_path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create CSV
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Staff Name', 'Rank', 'Session', 'Date', 'Status', 
            'Check In Time', 'QR Code Scanned', 'Location Verified'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for record in queryset:
            writer.writerow({
                'Staff Name': record.staff.full_name,
                'Rank': record.staff.get_rank_display(),
                'Session': record.session.title,
                'Date': record.session.date.strftime('%Y-%m-%d'),
                'Status': record.get_status_display(),
                'Check In Time': record.check_in_time.strftime('%H:%M') if record.check_in_time else 'N/A',
                'QR Code Scanned': 'Yes' if record.qr_code_scanned else 'No',
                'Location Verified': 'Yes' if record.location_verified else 'No'
            })
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    return file_path, file_size


def generate_staff_pdf_report(queryset, start_date, end_date):
    """Generate staff performance PDF report"""
    from django.conf import settings
    import os
    
    # Create filename
    filename = f"staff_performance_{start_date}_{end_date}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create PDF
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1
    )
    
    story.append(Paragraph("MSU-SND ROTC Staff Performance Report", title_style))
    story.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Create table data
    data = [['Staff Name', 'Rank', 'Specialization', 'Status', 'Date Assigned']]
    
    for staff in queryset:
        data.append([
            staff.user.full_name,
            staff.user.get_rank_display(),
            staff.get_specialization_display(),
            staff.get_status_display(),
            staff.date_assigned.strftime('%Y-%m-%d')
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    doc.build(story)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    return file_path, file_size


def generate_staff_excel_report(queryset, start_date, end_date):
    """Generate staff performance Excel report"""
    from django.conf import settings
    import os
    
    # Create filename
    filename = f"staff_performance_{start_date}_{end_date}.xlsx"
    file_path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create DataFrame
    data = []
    for staff in queryset:
        data.append({
            'Staff Name': staff.user.full_name,
            'Rank': staff.user.get_rank_display(),
            'Specialization': staff.get_specialization_display(),
            'Status': staff.get_status_display(),
            'Date Assigned': staff.date_assigned.strftime('%Y-%m-%d'),
            'Email': staff.user.email,
            'Contact Number': staff.user.contact_number or 'N/A',
            'Emergency Contact': staff.emergency_contact_name or 'N/A',
            'Emergency Contact Number': staff.emergency_contact_number or 'N/A'
        })
    
    df = pd.DataFrame(data)
    
    # Save to Excel
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Staff Performance', index=False)
        
        # Get worksheet for formatting
        worksheet = writer.sheets['Staff Performance']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    return file_path, file_size
