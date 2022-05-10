# Generated by Django 4.0.1 on 2022-05-09 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='system',
            name='configurations',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='system',
            name='storage',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='system',
            name='symbol_timeframe_pair',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
