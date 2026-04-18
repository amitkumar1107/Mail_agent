from django.urls import path

from .views import (
    command_page,
    contacts_page,
    dashboard_page,
    history_page,
    home,
    login_page,
    register_page,
    reminders_page,
)

urlpatterns = [
    path('', home, name='ui-home'),
    path('login/', login_page, name='ui-login'),
    path('register/', register_page, name='ui-register'),
    path('command/', command_page, name='ui-command'),
    path('contacts/', contacts_page, name='ui-contacts'),
    path('reminders/', reminders_page, name='ui-reminders'),
    path('history/', history_page, name='ui-history'),
    path('dashboard/', dashboard_page, name='ui-dashboard'),
]
