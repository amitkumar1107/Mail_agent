from django.db import migrations


def seed_system_templates(apps, schema_editor):
    EmailTemplate = apps.get_model('mail_templates', 'EmailTemplate')

    templates = [
        {
            'name': 'Birthday Classic',
            'category': 'birthday',
            'intent_key': 'birthday_wish',
            'subject_template': 'Happy Birthday, {name}!',
            'body_template': 'Dear {name},\n\nWishing you a very happy birthday and a fantastic year ahead.\n\nBest wishes,\n{sender}',
        },
        {
            'name': 'Thank You Note',
            'category': 'thank_you',
            'intent_key': 'thank_you',
            'subject_template': 'Thank You',
            'body_template': 'Dear {name},\n\nThank you for your support and help. I truly appreciate it.\n\nRegards,\n{sender}',
        },
        {
            'name': 'Formal Apology',
            'category': 'apology',
            'intent_key': 'apology',
            'subject_template': 'Sincere Apology',
            'body_template': 'Dear {name},\n\nI sincerely apologize for the inconvenience caused. Thank you for your understanding.\n\nRegards,\n{sender}',
        },
        {
            'name': 'Business Follow-up',
            'category': 'business',
            'intent_key': 'reminder',
            'subject_template': 'Follow-up on Our Discussion',
            'body_template': 'Dear {name},\n\nThis is a quick follow-up regarding our recent discussion. Please let me know the next steps.\n\nBest regards,\n{sender}',
        },
    ]

    for item in templates:
        EmailTemplate.objects.get_or_create(
            user=None,
            name=item['name'],
            defaults={
                'category': item['category'],
                'intent_key': item['intent_key'],
                'subject_template': item['subject_template'],
                'body_template': item['body_template'],
                'is_system': True,
                'is_active': True,
            },
        )


def unseed_system_templates(apps, schema_editor):
    EmailTemplate = apps.get_model('mail_templates', 'EmailTemplate')
    EmailTemplate.objects.filter(
        is_system=True,
        user=None,
        name__in=['Birthday Classic', 'Thank You Note', 'Formal Apology', 'Business Follow-up'],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mail_templates', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_system_templates, unseed_system_templates),
    ]
