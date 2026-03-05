from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import User, UserSession
from .serializers import UserSerializer, LoginSerializer
import json


def landing_view(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('authentication:dashboard')
    return render(request, 'landing.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username') or request.POST.get('email', '')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', 'staff')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check user type for admin login
            if user_type == 'admin' and user.role != 'admin':
                messages.error(request, 'Access denied. Administrator access required.')
                return JsonResponse({'success': False, 'error': 'Access denied. Administrator privileges required.'})
            
            # Check if staff trying to login as admin
            if user_type == 'staff' and user.role == 'admin':
                messages.error(request, 'Please use the Administrator login option.')
                return JsonResponse({'success': False, 'error': 'Please use the Administrator login option.'})
            
            login(request, user)
            
            # Create user session
            if request.session.session_key:
                UserSession.objects.create(
                    user=user,
                    session_key=request.session.session_key,
                    ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            
            messages.success(request, f'Welcome back, {user.full_name}!')
            
            # Redirect based on user role
            if user.role == 'admin':
                redirect_url = '/admin/'
            else:
                redirect_url = '/dashboard/'
            
            return JsonResponse({'success': True, 'redirect': redirect_url})
        else:
            messages.error(request, 'Invalid credentials.')
            return JsonResponse({'success': False, 'error': 'Invalid credentials. Please check your email and password.'})
    
    return render(request, 'authentication/login.html')


def staff_login_view(request):
    """Staff-specific login view — delegates to unified login page"""
    if request.method == 'POST':
        username = request.POST.get('username') or request.POST.get('email', '')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role == 'admin':
                return JsonResponse({'success': False, 'error': 'Please use the Administrator login option.'})
            
            login(request, user)
            if request.session.session_key:
                UserSession.objects.create(
                    user=user,
                    session_key=request.session.session_key,
                    ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            messages.success(request, f'Welcome back, {user.full_name}!')
            return JsonResponse({'success': True, 'redirect': '/dashboard/'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials.'})
    
    return redirect('authentication:login')


def admin_login_view(request):
    """Administrator-specific login view"""
    if request.method == 'POST':
        username = request.POST.get('username') or request.POST.get('email', '')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role != 'admin':
                return JsonResponse({'success': False, 'error': 'Access denied. Administrator privileges required.'})
            
            login(request, user)
            if request.session.session_key:
                UserSession.objects.create(
                    user=user,
                    session_key=request.session.session_key,
                    ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            messages.success(request, f'Welcome back, {user.full_name}!')
            return JsonResponse({'success': True, 'redirect': '/admin/'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials.'})
    
    return redirect('authentication:login')


@login_required
def logout_view(request):
    # Deactivate user session
    if request.session.session_key:
        UserSession.objects.filter(
            user=request.user,
            session_key=request.session.session_key
        ).update(is_active=False)
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('authentication:login')


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            
            # Create user session
            UserSession.objects.create(
                user=user,
                session_key=request.META.get('HTTP_SESSION_KEY', ''),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'success': True,
                'token': token.key,
                'user': UserSerializer(user).data
            })
        else:
            return Response({
                'success': False,
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    try:
        # Delete token
        request.user.auth_token.delete()
        
        # Deactivate user sessions
        UserSession.objects.filter(user=request.user).update(is_active=False)
        
        return Response({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Logout error for user {request.user}: {e}')
        return Response({'success': False, 'error': 'Error during logout'},
                       status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@login_required
def staff_management_view(request):
    """Staff management view for administrators"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('authentication:dashboard')
    return render(request, 'authentication/staff_management.html')


def about_view(request):
    """About page view"""
    return render(request, 'authentication/about.html')


@login_required
def dashboard_view(request):
    """Dashboard view"""
    return render(request, 'dashboard.html')


def staff_signup_view(request):
    """Staff registration view with QR code generation"""
    if request.method == 'POST':
        try:
            # Extract form data
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name', '')
            last_name = request.POST.get('last_name')
            suffix = request.POST.get('suffix', '')
            gender = request.POST.get('gender')
            rank = request.POST.get('rank')
            service_number = request.POST.get('service_number')
            birthdate = request.POST.get('birthdate')
            nationality = request.POST.get('nationality')
            religion = request.POST.get('religion', '')
            cell_number = request.POST.get('cell_number')
            facebook = request.POST.get('facebook', '')
            address = request.POST.get('address')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            emergency_name = request.POST.get('emergency_name', '')
            emergency_number = request.POST.get('emergency_number', '')
            emergency_relationship = request.POST.get('emergency_relationship', '')
            
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'Username already exists'})
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'Email already exists'})
            if User.objects.filter(service_number=service_number).exists():
                return JsonResponse({'success': False, 'error': 'Service number already exists'})
            
            # Create full name
            full_name = f"{first_name} {middle_name} {last_name}".strip()
            if suffix:
                full_name += f" {suffix}"
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                service_number=service_number,
                rank=rank,
                role='staff',
                is_active=True,
                is_staff=False,
                is_superuser=False
            )
            
            # Create QR code data
            qr_data = {
                'user_id': str(user.id),
                'service_number': service_number,
                'rank': rank,
                'full_name': full_name,
                'email': email,
                'type': 'staff_attendance'
            }
            
            # Generate QR code (implementation depends on your QR code library)
            import qrcode
            import io
            import base64
            from django.core.files.base import ContentFile
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_image = base64.b64encode(buffer.getvalue()).decode()
            
            # Store QR code in user profile or separate model
            # For now, return it in response
            return JsonResponse({
                'success': True,
                'qr_code_url': f'data:image/png;base64,{qr_image}',
                'full_name': full_name,
                'service_number': service_number,
                'rank': rank
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception('Error in staff signup')
            return JsonResponse({'success': False, 'error': 'An error occurred during registration. Please try again.'})
    
    return render(request, 'authentication/staff_signup.html')


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
