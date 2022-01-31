from django.contrib import admin
from .models import RunnerStatus

class AdminRunnerStatus(admin.ModelAdmin):
    list_display = (
        "enable",
        "enable_finviz",
        "enable_strategies",
        "loop_wait",
        "last_run_time",
    )

admin.site.register(RunnerStatus, AdminRunnerStatus)