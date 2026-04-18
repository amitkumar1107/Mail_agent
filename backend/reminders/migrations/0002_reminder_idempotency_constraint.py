from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('reminders', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='reminder',
            constraint=models.UniqueConstraint(
                fields=('user', 'idempotency_key'),
                condition=~Q(idempotency_key=''),
                name='uniq_nonempty_reminder_idempotency_per_user',
            ),
        ),
    ]
