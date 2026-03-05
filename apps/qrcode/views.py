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
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_M
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import json
import uuid
from datetime import timedelta

from apps.attendance.models import TrainingSession, AttendanceQRCode, AttendanceRecord
from apps.authentication.models import User
from .models import QRCodeTemplate, QRCodeLog, QRCodeScanAttempt
from .serializers import QRCodeTemplateSerializer, AttendanceQRCodeSerializer


@login_required
def qr_code_generator(request):
    """QR Code generation page"""
    sessions = TrainingSession.objects.filter(status='scheduled').order_by('date', 'start_time')
    templates = QRCodeTemplate.objects.filter(is_active=True)
    
    context = {
        'sessions': sessions,
        'templates': templates,
    }
    return render(request, 'qrcode/generator.html', context)


@login_required
def qr_code_scanner(request):
    """QR Code scanning page"""
    return render(request, 'qrcode/scanner.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_qr_code(request):
    """Generate QR code for attendance"""
    session_id = request.data.get('session_id')
    template_id = request.data.get('template_id')
    expires_minutes = request.data.get('expires_minutes', 60)
    max_scans = request.data.get('max_scans', 100)
    
    try:
        session = TrainingSession.objects.get(id=session_id)
        template = QRCodeTemplate.objects.get(id=template_id) if template_id else None
        
        # Generate unique QR code data
        qr_data = {
            'session_id': str(session.id),
            'timestamp': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(minutes=expires_minutes)).isoformat(),
            'unique_id': str(uuid.uuid4())
        }
        
        qr_string = json.dumps(qr_data)
        
        # Create QR code image
        qr = QRCode(
            version=1,
            error_correction=ERROR_CORRECT_M,
            box_size=template.box_size if template else 10,
            border=template.border if template else 4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        # Create QR code image
        if template:
            qr_img = qr.make_image(
                fill_color=template.foreground_color,
                back_color=template.background_color
            )
        else:
            qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Add logo if template has one
        if template and template.logo:
            logo = Image.open(template.logo.path)
            qr_img = add_logo_to_qr(qr_img, logo)
        
        # Convert to base64 for storage
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Save QR code to database
        attendance_qr = AttendanceQRCode.objects.create(
            session=session,
            qr_code_data=qr_string,
            qr_code_image=f"data:image/png;base64,{qr_image_base64}",
            expires_at=timezone.now() + timedelta(minutes=expires_minutes),
            max_scans=max_scans,
            created_by=request.user
        )
        
        # Log the generation
        QRCodeLog.objects.create(
            qr_code=attendance_qr,
            action='generated',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        serializer = AttendanceQRCodeSerializer(attendance_qr)
        return Response({
            'success': True,
            'qr_code': serializer.data,
            'qr_image': qr_image_base64
        })
        
    except TrainingSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Training session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except QRCodeTemplate.DoesNotExist:
        return Response({
            'success': False,
            'error': 'QR code template not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error generating QR code')
        return Response({
            'success': False,
            'error': 'An error occurred while generating the QR code. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scan_qr_code(request):
    """Process QR code scan for attendance"""
    qr_data = request.data.get('qr_data')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    try:
        # Parse QR code data
        qr_json = json.loads(qr_data)
        session_id = qr_json.get('session_id')
        expires_at_str = qr_json.get('expires_at')
        
        # Check if QR code is expired
        expires_at = timezone.datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
        if timezone.now() > expires_at:
            QRCodeScanAttempt.objects.create(
                qr_code_data=qr_data,
                staff=request.user,
                status='expired',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                location_data={'latitude': latitude, 'longitude': longitude} if latitude and longitude else None
            )
            return Response({
                'success': False,
                'error': 'QR code has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find the QR code in database
        try:
            attendance_qr = AttendanceQRCode.objects.get(
                qr_code_data=qr_data,
                is_active=True
            )
        except AttendanceQRCode.DoesNotExist:
            QRCodeScanAttempt.objects.create(
                qr_code_data=qr_data,
                staff=request.user,
                status='invalid',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                location_data={'latitude': latitude, 'longitude': longitude} if latitude and longitude else None
            )
            return Response({
                'success': False,
                'error': 'Invalid QR code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if max scans reached
        if attendance_qr.scan_count >= attendance_qr.max_scans:
            return Response({
                'success': False,
                'error': 'QR code scan limit reached'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already has attendance record for this session
        try:
            existing_record = AttendanceRecord.objects.get(
                session=attendance_qr.session,
                staff=request.user
            )
            QRCodeScanAttempt.objects.create(
                qr_code_data=qr_data,
                staff=request.user,
                status='duplicate',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                location_data={'latitude': latitude, 'longitude': longitude} if latitude and longitude else None
            )
            return Response({
                'success': False,
                'error': 'Attendance already marked for this session'
            }, status=status.HTTP_400_BAD_REQUEST)
        except AttendanceRecord.DoesNotExist:
            pass
        
        # Create attendance record
        attendance_record = AttendanceRecord.objects.create(
            session=attendance_qr.session,
            staff=request.user,
            status='present',
            check_in_time=timezone.now(),
            qr_code_scanned=True,
            qr_code_scan_time=timezone.now(),
            location_verified=bool(latitude and longitude),
            marked_by=request.user
        )
        
        # Update QR code scan count
        attendance_qr.scan_count += 1
        attendance_qr.save()
        
        # Log the scan
        QRCodeLog.objects.create(
            qr_code=attendance_qr,
            action='scanned',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            location_data={'latitude': latitude, 'longitude': longitude} if latitude and longitude else None
        )
        
        # Log successful scan attempt
        QRCodeScanAttempt.objects.create(
            qr_code_data=qr_data,
            staff=request.user,
            status='success',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            location_data={'latitude': latitude, 'longitude': longitude} if latitude and longitude else None
        )
        
        return Response({
            'success': True,
            'message': 'Attendance marked successfully',
            'session': attendance_qr.session.title,
            'check_in_time': attendance_record.check_in_time.isoformat()
        })
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid QR code format'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error scanning QR code')
        return Response({
            'success': False,
            'error': 'An error occurred while processing the QR code. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def qr_code_list(request):
    """List QR codes for sessions"""
    session_id = request.query_params.get('session_id')
    
    if session_id:
        qr_codes = AttendanceQRCode.objects.filter(session_id=session_id).order_by('-created_at')
    else:
        qr_codes = AttendanceQRCode.objects.all().order_by('-created_at')
    
    serializer = AttendanceQRCodeSerializer(qr_codes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_qr_code(request, qr_code_id):
    """Deactivate a QR code"""
    try:
        qr_code = AttendanceQRCode.objects.get(id=qr_code_id)
        qr_code.is_active = False
        qr_code.save()
        
        # Log the deactivation
        QRCodeLog.objects.create(
            qr_code=qr_code,
            action='deactivated',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'success': True, 'message': 'QR code deactivated'})
        
    except AttendanceQRCode.DoesNotExist:
        return Response({
            'success': False,
            'error': 'QR code not found'
        }, status=status.HTTP_404_NOT_FOUND)


def add_logo_to_qr(qr_img, logo, size_ratio=0.2):
    """Add logo to QR code"""
    qr_width, qr_height = qr_img.size
    logo_size = int(qr_width * size_ratio)
    
    # Resize logo
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    # Calculate position to center the logo
    pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
    
    # Create a white background for the logo
    logo_bg = Image.new('RGBA', (logo_size + 20, logo_size + 20), (255, 255, 255, 255))
    logo_bg.paste(logo, (10, 10))
    
    # Paste logo onto QR code
    qr_img.paste(logo_bg, pos, logo_bg)
    
    return qr_img
