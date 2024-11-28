# Generated by Django 5.1.2 on 2024-11-28 03:26

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('transport', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('roll_num', models.CharField(max_length=9, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(message='Roll number must be in the format XXk-XXXX, e.g., 22K-4586.', regex='^\\d{2}[A-Z]-\\d{4}$')])),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('Address', models.CharField(max_length=200)),
                ('cnic', models.CharField(max_length=13, unique=True)),
                ('contact', models.CharField(max_length=11)),
                ('emergency_contact', models.CharField(max_length=11)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'N/S')], default='male', max_length=10)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profiles')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('assigned_route', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='transport.route')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='userauth.department')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
