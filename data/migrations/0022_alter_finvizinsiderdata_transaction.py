# Generated by Django 4.0.1 on 2022-02-03 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0021_finvizinsiderdatafile_finvizinsiderdata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finvizinsiderdata',
            name='transaction',
            field=models.CharField(blank=True, choices=[('Buy', 'Buy'), ('Sale', 'Sale'), ('Option Exercise', 'Option Exercise')], default=None, max_length=200, null=True),
        ),
    ]