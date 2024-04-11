# Generated by Django 4.2 on 2024-04-11 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clearance', '0004_clearance_progress'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrativeapproval',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='clerkapproval',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='deptapproval',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='labapproval',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
    ]