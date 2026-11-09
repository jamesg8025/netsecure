from django.urls import path

from . import auth_views, views

app_name = 'api'

urlpatterns = [
    path('health/', views.health, name='health'),
    path('csrf/', views.csrf, name='csrf'),
    path('auth/login/', auth_views.login, name='auth-login'),
    path('auth/logout/', auth_views.logout, name='auth-logout'),
    path('auth/me/', auth_views.me, name='auth-me'),
    path('scans/', views.scans, name='scans'),
    path('scans/<int:scan_id>/devices/', views.scan_devices, name='scan-devices'),
    path('scans/<int:scan_id>/findings/', views.scan_findings, name='scan-findings'),
]
