# Generated by Django 4.2 on 2024-04-17 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clearance', '0007_alter_administrativeapproval_admin_role'),
        ('accounts', '0005_alter_adminaccount_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminaccount',
            name='dept',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='clearance.department'),
        ),
    ]
