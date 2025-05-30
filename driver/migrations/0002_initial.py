# Generated by Django 5.1.2 on 2024-11-30 22:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('driver', '0001_initial'),
        ('transport', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='appointed_provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drivers', to='transport.transportprovider'),
        ),
        migrations.AddField(
            model_name='driver',
            name='appointed_vehicle',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='transport.vehicle'),
        ),
        migrations.AddField(
            model_name='driver',
            name='registration_status',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='driver.driverstatus'),
        ),
    ]
