# Generated by Django 4.0.1 on 2022-05-23 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0003_broker_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='broker',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='broker',
            name='broker_class',
            field=models.CharField(choices=[('InteractiveBrokers', 'InteractiveBrokers'), ('IG', 'IG')], max_length=50),
        ),
    ]