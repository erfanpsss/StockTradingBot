# Generated by Django 4.0.1 on 2022-04-19 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('strategy', '0004_alter_strategy_options_alter_strategy_broker_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='strategy',
            old_name='strategy_configuration',
            new_name='configurations',
        ),
        migrations.RenameField(
            model_name='strategy',
            old_name='active',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='strategy',
            old_name='strategy_storage',
            new_name='storage',
        ),
        migrations.RemoveField(
            model_name='strategy',
            name='broker',
        ),
        migrations.RemoveField(
            model_name='strategy',
            name='risk_management',
        ),
        migrations.RemoveField(
            model_name='strategy',
            name='symbol_timeframe_pair',
        ),
        migrations.DeleteModel(
            name='RiskManagement',
        ),
    ]
