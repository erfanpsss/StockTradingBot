# Generated by Django 4.0.1 on 2022-02-14 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0006_alter_trade_position_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='sent_arguments',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
