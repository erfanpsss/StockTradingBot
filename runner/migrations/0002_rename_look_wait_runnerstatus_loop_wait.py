# Generated by Django 4.0.1 on 2022-01-31 11:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('runner', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runnerstatus',
            old_name='look_wait',
            new_name='loop_wait',
        ),
    ]