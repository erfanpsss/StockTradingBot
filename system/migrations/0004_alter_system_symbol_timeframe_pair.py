# Generated by Django 4.0.1 on 2022-05-13 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0003_alter_system_symbol_timeframe_pair'),
    ]

    operations = [
        migrations.AlterField(
            model_name='system',
            name='symbol_timeframe_pair',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
