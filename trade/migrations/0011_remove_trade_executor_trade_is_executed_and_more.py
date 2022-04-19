# Generated by Django 4.0.1 on 2022-03-06 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0010_trade_created_at_trade_order_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trade',
            name='executor',
        ),
        migrations.AddField(
            model_name='trade',
            name='is_executed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='trade',
            name='trade_type',
            field=models.CharField(choices=[('Open', 'Open'), ('Close', 'Close')], default='Open', max_length=10),
        ),
    ]