# Generated by Django 4.0.1 on 2022-04-18 07:33

from django.db import migrations, models
import django.db.models.deletion
import strategy.models


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0011_broker_buying_power'),
        ('strategy', '0003_strategy_broker'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='strategy',
            options={'verbose_name': 'Trading System', 'verbose_name_plural': 'Trading Systems'},
        ),
        migrations.AlterField(
            model_name='strategy',
            name='broker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='broker_risk_managements', to='broker.broker'),
        ),
        migrations.CreateModel(
            name='RiskManagement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('active', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('symbol_timeframe_pair', models.JSONField(default=strategy.models.default_symbol_timeframe_pair)),
                ('indicators_configuration', models.JSONField(default=strategy.models.default_indicators_configuration)),
                ('risk_management_configuration', models.JSONField(blank=True, default=dict, null=True)),
                ('risk_management_class', models.CharField(choices=[('SampleRiskManagement', 'SampleRiskManagement'), ('Alpha', 'Alpha')], max_length=200)),
                ('risk_management_storage', models.JSONField(blank=True, default=dict, null=True)),
                ('broker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='broker_strategies', to='broker.broker')),
            ],
            options={
                'verbose_name': 'Trading System',
                'verbose_name_plural': 'Trading Systems',
            },
        ),
        migrations.AddField(
            model_name='strategy',
            name='risk_management',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='strategy_risk_managements', to='strategy.riskmanagement'),
        ),
    ]
