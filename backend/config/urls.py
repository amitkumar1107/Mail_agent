from django.contrib import admin
from django.urls import include, path

from .health import health_live, health_ready

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_live, name='health-live'),
    path('health/live/', health_live, name='health-live-v2'),
    path('health/ready/', health_ready, name='health-ready'),
    path('api/auth/', include('accounts.urls')),
    path('api/contacts/', include('contacts.urls')),
    path('api/mail/', include('mail_core.urls')),
    path('api/templates/', include('mail_templates.urls')),
    path('api/voice/', include('voice.urls')),
    path('api/reminders/', include('reminders.urls')),
]
