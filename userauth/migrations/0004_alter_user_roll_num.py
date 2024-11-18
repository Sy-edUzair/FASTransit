# Generated by Django 5.1.2 on 2024-11-18 03:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0003_alter_user_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='roll_num',
            field=models.CharField(max_length=9, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(message='Roll number must be in the format XXk-XXXX, e.g., 22k-4586.', regex='^\\d{2}[A-Z]-\\d{4}$')]),
        ),
    ]
