from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mail_core', '0002_commandhistory_ai_error_commandhistory_ai_raw_output_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='emaildraft',
            index=models.Index(fields=['user', 'status', 'created_at'], name='mail_core_e_user_id_42bd84_idx'),
        ),
        migrations.AddIndex(
            model_name='sentemaillog',
            index=models.Index(fields=['user', 'result', 'sent_at'], name='mail_core_s_user_id_eca1ea_idx'),
        ),
        migrations.AddIndex(
            model_name='sentemaillog',
            index=models.Index(fields=['user', 'recipient_email'], name='mail_core_s_user_id_0ee7ba_idx'),
        ),
        migrations.AddIndex(
            model_name='commandhistory',
            index=models.Index(fields=['user', 'created_at'], name='mail_core_c_user_id_03bebd_idx'),
        ),
        migrations.AddIndex(
            model_name='commandhistory',
            index=models.Index(fields=['user', 'parsed_intent', 'parsed_action'], name='mail_core_c_user_id_0c8bdb_idx'),
        ),
    ]
