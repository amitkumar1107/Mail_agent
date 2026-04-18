import os
from dataclasses import dataclass

from django.core.mail import EmailMessage


@dataclass
class EmailSendResult:
    success: bool
    provider: str
    message_id: str
    error: str = ''


class BaseEmailProvider:
    provider_name = 'base'

    def send(self, to_email: str, subject: str, body: str) -> EmailSendResult:
        raise NotImplementedError


class DjangoSMTPProvider(BaseEmailProvider):
    provider_name = 'django_smtp'

    def send(self, to_email: str, subject: str, body: str) -> EmailSendResult:
        try:
            count = EmailMessage(subject=subject, body=body, to=[to_email]).send(fail_silently=False)
            return EmailSendResult(True, self.provider_name, str(count))
        except Exception as exc:
            return EmailSendResult(False, self.provider_name, '', str(exc))


class BrevoProvider(DjangoSMTPProvider):
    provider_name = 'brevo'


class GmailProvider(DjangoSMTPProvider):
    provider_name = 'gmail'


def get_email_provider() -> BaseEmailProvider:
    key = os.getenv('EMAIL_PROVIDER', 'django').lower().strip()
    if key == 'brevo':
        return BrevoProvider()
    if key == 'gmail':
        return GmailProvider()
    return DjangoSMTPProvider()


def send_email_with_provider(to_email: str, subject: str, body: str) -> EmailSendResult:
    provider = get_email_provider()
    return provider.send(to_email=to_email, subject=subject, body=body)
