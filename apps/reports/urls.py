from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register(r'reports', views.ReportViewSet)
router.register(r'schedules', views.ReportScheduleViewSet)

app_name = 'reports'

urlpatterns = [
    # Web views
    path('', views.reports_dashboard, name='dashboard'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/generate/attendance/', views.generate_attendance_report, name='generate_attendance'),
    path('api/generate/staff-performance/', views.generate_staff_performance_report, name='generate_staff_performance'),
    path('api/download/<uuid:report_id>/', views.download_report, name='download'),
]
