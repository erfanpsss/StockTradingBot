# Generated by Django 4.0.1 on 2022-05-10 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0003_rename_main_quanity_trade_main_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='trade_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
