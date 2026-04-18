from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone


def health_live(_request):
    return JsonResponse({'status': 'ok', 'timestamp': timezone.now().isoformat()})


def health_ready(_request):
    checks = {'db': False, 'cache': False}
    status_code = 200

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        checks['db'] = True
    except Exception:
        status_code = 503

    try:
        cache.set('health_check', 'ok', timeout=5)
        checks['cache'] = cache.get('health_check') == 'ok'
        if not checks['cache']:
            status_code = 503
    except Exception:
        status_code = 503

    payload = {
        'status': 'ok' if status_code == 200 else 'degraded',
        'checks': checks,
        'timestamp': timezone.now().isoformat(),
    }
    return JsonResponse(payload, status=status_code)
