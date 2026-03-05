from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register(r'staff', views.TrainingStaffViewSet)
router.register(r'qualifications', views.StaffQualificationViewSet)
router.register(r'performance', views.StaffPerformanceViewSet)
router.register(r'schedules', views.StaffScheduleViewSet)

app_name = 'staff'

urlpatterns = [
    # Web views
    path('', views.staff_list, name='list'),
    path('<uuid:staff_id>/', views.staff_detail, name='detail'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/stats/', views.staff_stats, name='stats'),
    path('api/create-profile/', views.create_staff_profile, name='create_profile'),
    path('api/<uuid:staff_id>/update-status/', views.update_staff_status, name='update_status'),
    path('api/schedule/', views.staff_schedule, name='schedule'),
    path('api/schedule/create/', views.create_schedule, name='create_schedule'),
]
