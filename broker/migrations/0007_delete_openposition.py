# Generated by Django 4.0.1 on 2022-02-10 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0006_openposition'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OpenPosition',
        ),
    ]