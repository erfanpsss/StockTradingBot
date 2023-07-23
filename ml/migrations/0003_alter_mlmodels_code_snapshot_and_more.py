# Generated by Django 4.0.1 on 2023-07-23 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0002_rename_created_at_mlmodels_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mlmodels',
            name='code_snapshot',
            field=models.FileField(null=True, upload_to='ml_models_code'),
        ),
        migrations.AlterField(
            model_name='mlmodels',
            name='model_type',
            field=models.CharField(blank=True, choices=[('RandomForestClassifier', 'Randomforestclassifier'), ('LogisticRegression', 'Logisticregression'), ('NeuralNetwork', 'Neuralnetwork'), ('XgBoost', 'Xgboost')], max_length=50, null=True),
        ),
    ]
