# Generated by Django 4.2 on 2024-04-07 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentaccount',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentaccount',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
