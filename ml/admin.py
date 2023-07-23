from django.contrib import admin
from .models import MlModels


@admin.register(MlModels)
class AdminMlModels(admin.ModelAdmin):
    list_display = ("id", "created_at", "model_type", "report")
    list_filter = ("model_type",)
    search_fields = ("model_type", "report")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "model_type", "report")
    fieldsets = (
        ("Model", {"fields": ("model_type", "report")}),
        ("Data", {"fields": ("data_snapshot", "code_snapshot")}),
        ("Created at", {"fields": ("created_at",)}),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
