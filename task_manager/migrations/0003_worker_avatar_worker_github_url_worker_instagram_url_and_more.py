# Generated by Django 4.2.11 on 2024-03-12 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0002_alter_worker_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='avatar',
            field=models.ImageField(default='media/avatars/default_user.png', upload_to='media/avatars'),
        ),
        migrations.AddField(
            model_name='worker',
            name='github_url',
            field=models.CharField(default='Uknown', max_length=255),
        ),
        migrations.AddField(
            model_name='worker',
            name='instagram_url',
            field=models.CharField(default='Uknown', max_length=255),
        ),
        migrations.AddField(
            model_name='worker',
            name='linkedin_url',
            field=models.CharField(default='Uknown', max_length=255),
        ),
        migrations.AddField(
            model_name='worker',
            name='telegram_url',
            field=models.CharField(default='Uknown', max_length=255),
        ),
    ]