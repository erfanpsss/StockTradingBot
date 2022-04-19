# Generated by Django 4.0.1 on 2022-03-06 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0011_broker_buying_power'),
        ('strategy', '0002_strategy_symbol_timeframe_pair_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategy',
            name='broker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='broker_strategies', to='broker.broker'),
            preserve_default=False,
        ),
    ]