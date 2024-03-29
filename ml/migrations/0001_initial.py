# Generated by Django 4.0.1 on 2023-07-22 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MlModels',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_At', models.DateTimeField(auto_now_add=True)),
                ('model', models.FileField(upload_to='ml_models')),
                ('code_snapshot', models.TextField(blank=True, null=True)),
                ('data_snapshot', models.FileField(upload_to='ml_models_data')),
                ('model_type', models.CharField(blank=True, choices=[('RandomForestClassifier', 'Randomforestclassifier'), ('LogisticRegression', 'Logisticregression'), ('NeuralNetwork', 'Neuralnetwork')], max_length=50, null=True)),
                ('report', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
