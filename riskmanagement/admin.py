from django.contrib import admin
from .models import RiskManagement


class AdminRiskManagement(admin.ModelAdmin):
    pass


admin.site.register(RiskManagement, AdminRiskManagement)
