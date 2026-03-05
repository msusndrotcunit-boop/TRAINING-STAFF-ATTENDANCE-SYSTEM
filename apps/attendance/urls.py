from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register(r'sessions', views.TrainingSessionViewSet)
router.register(r'records', views.AttendanceRecordViewSet)
router.register(r'qrcodes', views.AttendanceQRCodeViewSet)
router.register(r'summaries', views.AttendanceSummaryViewSet)

app_name = 'attendance'

urlpatterns = [
    # Web views
    path('', views.attendance_dashboard, name='dashboard'),
    path('session/<uuid:session_id>/', views.session_attendance, name='session_detail'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/stats/', views.attendance_stats, name='stats'),
    path('api/mark/', views.mark_attendance, name='mark'),
    path('api/bulk-mark/', views.bulk_mark_attendance, name='bulk_mark'),
    path('api/session/<uuid:session_id>/', views.session_attendance_list, name='session_list'),
    path('api/generate-summary/', views.generate_attendance_summary, name='generate_summary'),
]
