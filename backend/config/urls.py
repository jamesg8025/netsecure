"""
URL configuration for the NetSecure backend.

All REST endpoints live under /api/ and are defined in api/urls.py.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
