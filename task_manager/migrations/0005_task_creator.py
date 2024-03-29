# Generated by Django 4.2.11 on 2024-03-16 10:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0004_alter_worker_avatar_commentary'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='creator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='own_tasks', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
