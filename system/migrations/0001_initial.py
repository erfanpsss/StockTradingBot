# Generated by Django 4.0.1 on 2022-05-15 08:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('broker', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('riskmanagement', '0001_initial'),
        ('strategy', '0001_initial'),
        ('trademanagement', '0001_initial'),
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('is_active_manual_trade_handling', models.BooleanField(default=True)),
                ('is_active_automatic_trade_handling', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('symbol_timeframe_pair', models.JSONField(blank=True, default=list, null=True)),
                ('configurations', models.JSONField(blank=True, default=dict, null=True)),
                ('storage', models.JSONField(blank=True, default=dict, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_systems', to=settings.AUTH_USER_MODEL)),
                ('base_timeframe', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='system_timeframes', to='data.timeframe')),
                ('broker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='system_brokers', to='broker.broker')),
                ('risk_management', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='system_risk_managements', to='riskmanagement.riskmanagement')),
                ('strategy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='system_strategies', to='strategy.strategy')),
                ('trade_management', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='system_trade_managements', to='trademanagement.trademanagement')),
            ],
            options={
                'verbose_name': 'System',
                'verbose_name_plural': 'Systems',
            },
        ),
    ]
