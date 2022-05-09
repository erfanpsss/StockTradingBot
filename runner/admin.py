from django.contrib import admin
from .models import RunnerStatus


class AdminRunnerStatus(admin.ModelAdmin):
    list_display = (
        "enable",
        "enable_broker_scheduled_calls",
        "enable_finviz",
        "enable_systems",
        "loop_wait",
        "last_run_time",
    )


admin.site.register(RunnerStatus, AdminRunnerStatus)
