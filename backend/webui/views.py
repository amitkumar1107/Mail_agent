from django.shortcuts import redirect, render


def home(_request):
    return redirect('ui-command')


def login_page(request):
    return render(request, 'webui/login.html')


def register_page(request):
    return render(request, 'webui/register.html')


def command_page(request):
    return render(request, 'webui/command.html')


def contacts_page(request):
    return render(request, 'webui/contacts.html')


def reminders_page(request):
    return render(request, 'webui/reminders.html')


def history_page(request):
    return render(request, 'webui/history.html')


def dashboard_page(request):
    return render(request, 'webui/dashboard.html')
