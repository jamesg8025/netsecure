from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('health/', views.health, name='health'),
    path('csrf/', views.csrf, name='csrf'),
    path('scans/', views.scans, name='scans'),
    path('scans/<int:scan_id>/devices/', views.scan_devices, name='scan-devices'),
    path('scans/<int:scan_id>/findings/', views.scan_findings, name='scan-findings'),
]
