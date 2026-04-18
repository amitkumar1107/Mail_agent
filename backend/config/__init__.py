try:
    from .celery import app as celery_app
except ModuleNotFoundError:  # Allows manage.py commands in minimal environments.
    celery_app = None

__all__ = ('celery_app',)
