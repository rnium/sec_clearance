# Generated by Django 4.2 on 2024-05-05 17:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clearance', '0010_alter_department_dept_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lab',
            options={'ordering': ['id']},
        ),
    ]
