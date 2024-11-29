# Generated by Django 5.1.2 on 2024-11-29 19:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ComplaintStatus',
            fields=[
                ('status_id', models.AutoField(primary_key=True, serialize=False)),
                ('status_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('date_posted', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.TextField()),
                ('rating', models.IntegerField()),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('complaint_status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='noticeboard.complaintstatus')),
            ],
        ),
    ]
