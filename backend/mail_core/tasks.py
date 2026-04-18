import logging

from celery import shared_task
from django.contrib.auth.models import User

from .email_providers import send_email_with_provider
from .models import EmailDraft, SentEmailLog


logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_draft_email_task(self, draft_id: int, user_id: int):
    draft = EmailDraft.objects.filter(id=draft_id, user_id=user_id).first()
    if draft is None:
        logger.warning('send_draft_task_missing_draft', extra={'draft_id': draft_id, 'user_id': user_id})
        return {'status': 'missing_draft'}

    if draft.status == EmailDraft.STATUS_SENT:
        return {'status': 'already_sent'}
    if draft.status == EmailDraft.STATUS_CANCELED:
        return {'status': 'canceled'}

    result = send_email_with_provider(
        to_email=draft.recipient_email,
        subject=draft.subject,
        body=draft.body,
    )

    if not result.success:
        SentEmailLog.objects.create(
            user_id=user_id,
            draft=draft,
            recipient_email=draft.recipient_email,
            subject=draft.subject,
            body=draft.body,
            result=SentEmailLog.RESULT_FAILED,
            error_message=result.error or 'Email provider failed',
        )
        raise RuntimeError(result.error or 'Email provider failed')

    draft.status = EmailDraft.STATUS_SENT
    draft.save(update_fields=['status', 'updated_at'])

    sent_log = SentEmailLog.objects.create(
        user_id=user_id,
        draft=draft,
        recipient_email=draft.recipient_email,
        subject=draft.subject,
        body=draft.body,
        result=SentEmailLog.RESULT_SUCCESS,
        provider_message_id=f'{result.provider}:{result.message_id}',
    )

    return {'status': 'sent', 'sent_log_id': sent_log.id}
