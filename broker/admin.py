from django.contrib import admin
from .models import Broker


class AdminBroker(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        "id",
        "user",
        "name",
        "account_id",
        "is_sandbox",
        "public_key",
        "secret_key",
        "broker_class",
        "storage",
        "balance",
        "equity",
        "used_margin",
        "connected", 
        "error",
    )
    list_filter = (
        "user",
        "name",
        "is_sandbox",
        "connected", 
    )
    search_fields = (
        "user",
        "name",
        "is_sandbox",
    )


admin.site.register(Broker, AdminBroker)
