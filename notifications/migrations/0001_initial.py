# Generated by Django 5.2 on 2025-04-03 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('TASK_OVERDUE', 'Task Overdue'), ('USER_DEACTIVATED', 'User Deactivated'), ('TASK_COMPLETED', 'Task Completed')], max_length=20)),
                ('message', models.TextField()),
                ('read', models.BooleanField(default=False)),
                ('related_task_id', models.IntegerField(blank=True, null=True)),
                ('related_user_id', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
