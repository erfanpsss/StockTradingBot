# Generated by Django 4.0.1 on 2022-03-05 03:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0009_trade_place_now_alter_trade_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trade',
            name='order_type',
            field=models.CharField(choices=[('LMT', 'LMT'), ('MKT', 'MKT'), ('STP', 'STP'), ('STOP_LIMIT', 'STOP_LIMIT'), ('MIDPRICE', 'MIDPRICE')], default='MKT', max_length=10),
        ),
    ]