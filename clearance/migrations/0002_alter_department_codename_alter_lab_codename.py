# Generated by Django 4.2 on 2024-04-06 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clearance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='codename',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='lab',
            name='codename',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
