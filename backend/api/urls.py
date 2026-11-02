from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('health/', views.health, name='health'),
    path('csrf/', views.csrf, name='csrf'),
    path('scans/', views.scans, name='scans'),
]
