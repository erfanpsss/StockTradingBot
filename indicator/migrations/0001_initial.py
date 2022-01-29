# Generated by Django 4.0.1 on 2022-01-19 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndicatorStorage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('indicator', models.TextField(unique=True)),
                ('storage', models.JSONField(blank=True, default=dict, null=True)),
            ],
            options={
                'verbose_name': 'Indicator storage',
                'verbose_name_plural': 'Indicator storages',
            },
        ),
        migrations.CreateModel(
            name='RelativeWickGrowthBasedPrice',
            fields=[
                ('sub_indicator_configuration', models.JSONField(blank=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('period', models.IntegerField()),
                ('value', models.FloatField()),
                ('up_wick', models.FloatField()),
                ('down_wick', models.FloatField()),
                ('candle_type', models.CharField(choices=[('HAMMER BEARISH', 'HAMMER BEARISH'), ('HAMMER BULLISH', 'HAMMER BULLISH'), ('UNKNOWN', 'UNKNOWN')], default='UNKNOWN', max_length=200)),
                ('price_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relative_wick_growth_based', to='data.data')),
            ],
            options={
                'unique_together': {('period', 'price_id')},
            },
        ),
        migrations.CreateModel(
            name='RelativeGrowthBasedPrice',
            fields=[
                ('sub_indicator_configuration', models.JSONField(blank=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('period', models.IntegerField()),
                ('value', models.FloatField()),
                ('price_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relative_growth_based', to='data.data')),
            ],
            options={
                'unique_together': {('period', 'price_id')},
            },
        ),
        migrations.CreateModel(
            name='NormalizePrice',
            fields=[
                ('sub_indicator_configuration', models.JSONField(blank=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('period', models.IntegerField()),
                ('value', models.FloatField()),
                ('price_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='normalize', to='data.data')),
            ],
            options={
                'unique_together': {('period', 'price_id')},
            },
        ),
        migrations.CreateModel(
            name='MovingAverage',
            fields=[
                ('sub_indicator_configuration', models.JSONField(blank=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('period', models.IntegerField()),
                ('value', models.FloatField()),
                ('price_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ma', to='data.data')),
            ],
            options={
                'unique_together': {('period', 'price_id')},
            },
        ),
        migrations.CreateModel(
            name='Macd',
            fields=[
                ('sub_indicator_configuration', models.JSONField(blank=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('long_period', models.IntegerField()),
                ('short_period', models.IntegerField()),
                ('signal_period', models.IntegerField()),
                ('value', models.FloatField()),
                ('signal', models.FloatField()),
                ('price_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='macd', to='data.data')),
            ],
            options={
                'unique_together': {('price_id', 'long_period', 'short_period', 'signal_period')},
            },
        ),
        migrations.CreateModel(
            name='LstmSignalGenerator',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('min_data_length', models.IntegerField(default=500)),
                ('max_data_length', models.IntegerField(blank=True, null=True)),
                ('remodel', models.BooleanField(default=False)),
                ('remodel_after', models.IntegerField(blank=True, null=True)),
                ('lag', models.IntegerField(default=7)),
                ('epoch', models.IntegerField(default=2000)),
                ('dense', models.IntegerField(default=1)),
                ('sub_indicator_configuration', models.JSONField()),
                ('output_configuration', models.JSONField()),
                ('output_value', models.TextField()),
                ('value', models.FloatField()),
                ('price_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lstm_signal_generator', to='data.data')),
            ],
            options={
                'unique_together': {('name', 'price_id')},
            },
        ),
        migrations.CreateModel(
            name='GrowthBasedPrice',
            fields=[
                ('sub_indicator_configuration', models.JSONField(blank=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('period', models.IntegerField()),
                ('value', models.FloatField()),
                ('price_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='growth_based', to='data.data')),
            ],
            options={
                'unique_together': {('period', 'price_id')},
            },
        ),
        migrations.CreateModel(
            name='ExponentialMovingAverage',
            fields=[
                ('sub_indicator_configuration', models.JSONField(blank=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('period', models.IntegerField()),
                ('value', models.FloatField()),
                ('price_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ema', to='data.data')),
            ],
            options={
                'unique_together': {('period', 'price_id')},
            },
        ),
        migrations.CreateModel(
            name='Atr',
            fields=[
                ('sub_indicator_configuration', models.JSONField(blank=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('period', models.IntegerField()),
                ('value', models.FloatField()),
                ('price_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='atr', to='data.data')),
            ],
            options={
                'unique_together': {('period', 'price_id')},
            },
        ),
    ]