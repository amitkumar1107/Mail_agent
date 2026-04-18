from datetime import datetime

from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Reminder
from .serializers import ReminderSerializer
from .tasks import process_due_reminders


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Reminder.objects.filter(user=self.request.user).select_related('contact')

        status_filter = self.request.query_params.get('status', '').strip()
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        date_from = self.request.query_params.get('date_from', '').strip()
        if date_from:
            try:
                dt = datetime.fromisoformat(date_from)
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
                queryset = queryset.filter(scheduled_for__gte=dt)
            except ValueError:
                pass

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='run-due')
    def run_due(self, request):
        # Useful for local/dev manual trigger in addition to beat schedules.
        process_due_reminders.delay()
        return Response({'message': 'Due reminder processor queued.'})
