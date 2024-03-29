# Generated by Django 4.2.11 on 2024-03-27 10:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("task_manager", "0009_alter_task_options_alter_worker_avatar"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="assignees",
            field=models.ManyToManyField(
                blank=True, related_name="tasks", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
