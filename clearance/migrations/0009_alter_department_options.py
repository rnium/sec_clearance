# Generated by Django 4.2 on 2024-04-22 06:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clearance', '0008_alter_department_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={'ordering': ['id']},
        ),
    ]
