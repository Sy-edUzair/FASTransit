# Generated by Django 5.1.2 on 2024-11-30 22:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payment', '0001_initial'),
        ('userauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='userauth.appuser'),
        ),
        migrations.AddField(
            model_name='payment',
            name='method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='payment.paymentmethod'),
        ),
        migrations.AddField(
            model_name='payment',
            name='receipt',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='payment.receipt'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='payment.paymentstatus'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vouchers', to='userauth.appuser'),
        ),
        migrations.AddField(
            model_name='payment',
            name='voucher',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vouchers', to='payment.voucher'),
        ),
    ]
