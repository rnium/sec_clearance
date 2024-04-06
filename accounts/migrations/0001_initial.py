# Generated by Django 4.2 on 2024-04-06 11:34

import accounts.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profiles/dp/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])),
                ('is_super_admin', models.BooleanField(default=False)),
                ('user_type', models.CharField(choices=[('principal', 'Principal'), ('academic', 'SEC Academic'), ('cashier', 'Cashier'), ('general', 'General Admin User')], default='general', max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InviteToken',
            fields=[
                ('id', models.CharField(default=accounts.models.InviteToken.get_uuid, editable=False, max_length=50, primary_key=True, serialize=False)),
                ('to_user_dept_id', models.IntegerField(blank=True, null=True)),
                ('user_email', models.EmailField(max_length=254)),
                ('actype', models.CharField(blank=True, max_length=10, null=True)),
                ('expiration', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='StudentAccount',
            fields=[
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profiles/dp/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])),
                ('registration', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'ordering': ['registration'],
            },
        ),
    ]
