# Generated by Django 5.1.2 on 2024-11-29 06:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0003_providerrepresentative_and_more'),
        ('userauth', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_type',
        ),
        migrations.DeleteModel(
            name='ProviderRepresentative',
        ),
    ]
