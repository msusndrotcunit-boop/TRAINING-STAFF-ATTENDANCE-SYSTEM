from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Web views
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('staff/login/', views.staff_login_view, name='staff_login'),
    path('staff/signup/', views.staff_signup_view, name='staff_signup'),
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('staff/management/', views.staff_management_view, name='staff_management'),
    path('about/', views.about_view, name='about'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # API endpoints
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/profile/', views.profile, name='profile'),
    path('api/profile/update/', views.update_profile, name='update_profile'),
]
