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

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


admin.site.register(RunnerStatus, AdminRunnerStatus)
