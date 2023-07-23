from django.db import models
from .choices import ModelType
from data.models import Symbol


class MlModels(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    model = models.FileField(upload_to="ml_models")
    symbol = models.ForeignKey(
        Symbol,
        on_delete=models.CASCADE,
        related_name="ml_models",
        null=True,
        blank=True,
    )
    code_snapshot = models.FileField(upload_to="ml_models_code", null=True)
    data_snapshot = models.FileField(upload_to="ml_models_data")
    model_type = models.CharField(
        max_length=50, blank=True, null=True, choices=ModelType.choices
    )
    report = models.TextField(blank=True, null=True)
