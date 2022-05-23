# Generated by Django 4.0.1 on 2022-05-15 08:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data', '0001_initial'),
        ('broker', '0001_initial'),
        ('system', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('place_now', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('PendingSubmit', 'PendingSubmit'), ('PendingCancel', 'PendingCancel'), ('PreSubmitted', 'PreSubmitted'), ('Cancelled', 'Cancelled'), ('Submitted', 'Submitted'), ('Filled', 'Filled'), ('Inactive', 'Inactive'), ('Failed', 'Failed')], default='PendingSubmit', max_length=50)),
                ('trade_type', models.CharField(choices=[('Open', 'Open'), ('Close', 'Close')], default='Open', max_length=10)),
                ('order_type', models.CharField(choices=[('LMT', 'LMT'), ('MKT', 'MKT'), ('STP', 'STP'), ('STOP_LIMIT', 'STOP_LIMIT'), ('MIDPRICE', 'MIDPRICE')], default='MKT', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('trade_datetime', models.DateTimeField(blank=True, null=True)),
                ('position_id', models.CharField(blank=True, max_length=200, null=True)),
                ('position_type', models.CharField(choices=[('buy', 'buy'), ('sell', 'sell')], max_length=10)),
                ('trade_price', models.FloatField(blank=True, null=True)),
                ('trade_size', models.FloatField(blank=True, null=True)),
                ('quantity', models.FloatField(blank=True, null=True)),
                ('main_quantity', models.FloatField(blank=True, null=True)),
                ('filled_quantity', models.FloatField(blank=True, null=True)),
                ('trade_stop_loss', models.FloatField(blank=True, null=True)),
                ('trade_limit', models.FloatField(blank=True, null=True)),
                ('is_executed', models.BooleanField(default=False)),
                ('closed_quantity', models.FloatField(blank=True, default=0.0, null=True)),
                ('sent_arguments', models.JSONField(blank=True, default=dict, null=True)),
                ('error', models.TextField(blank=True, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_trades', to=settings.AUTH_USER_MODEL)),
                ('broker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='broker_trades', to='broker.broker')),
                ('executor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='system_trades', to='system.system')),
                ('parent_trade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_trades', to='trade.trade')),
                ('price_data', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='data.data')),
                ('symbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trades', to='data.symbol')),
            ],
            options={
                'verbose_name': 'Trade',
                'verbose_name_plural': 'Trades',
            },
        ),
    ]
