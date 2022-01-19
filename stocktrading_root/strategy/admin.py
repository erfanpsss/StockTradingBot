from django.contrib import admin
from .models import Strategy


class AdminStrategy(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name",)
    search_fields = ("name",)


admin.site.register(Strategy, AdminStrategy)