# Generated by Django 4.2 on 2024-04-23 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clearance', '0010_alter_department_dept_type'),
        ('accounts', '0008_alter_studentaccount_registration'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentaccount',
            name='hall',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='clearance.department'),
        ),
    ]
