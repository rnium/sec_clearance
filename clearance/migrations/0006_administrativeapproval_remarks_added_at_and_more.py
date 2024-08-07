# Generated by Django 4.2 on 2024-04-17 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clearance', '0005_administrativeapproval_is_archived_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrativeapproval',
            name='remarks_added_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clerkapproval',
            name='remarks_added_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='department',
            name='clerk_title',
            field=models.CharField(default='Staff', max_length=100),
        ),
        migrations.AddField(
            model_name='department',
            name='head_title',
            field=models.CharField(default='Head', max_length=100),
        ),
        migrations.AddField(
            model_name='deptapproval',
            name='remarks_added_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='labapproval',
            name='remarks_added_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
