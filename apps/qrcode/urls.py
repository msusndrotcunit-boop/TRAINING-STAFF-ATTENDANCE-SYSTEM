from django.urls import path
from . import views

app_name = 'qrcode'

urlpatterns = [
    # Web views
    path('generator/', views.qr_code_generator, name='generator'),
    path('scanner/', views.qr_code_scanner, name='scanner'),
    
    # API endpoints
    path('api/generate/', views.generate_qr_code, name='api_generate'),
    path('api/scan/', views.scan_qr_code, name='api_scan'),
    path('api/list/', views.qr_code_list, name='api_list'),
    path('api/deactivate/<uuid:qr_code_id>/', views.deactivate_qr_code, name='api_deactivate'),
]
