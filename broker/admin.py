from attr import fields
from django.contrib import admin
from .models import Broker


class AdminBroker(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        "id",
        "user_account",
        "name",
        "account_id",
        "is_sandbox",
        "public_key",
        "secret_key",
        "broker_class",
        "balance",
        "equity",
        "buying_power",
        "used_margin",
        "connected",
        "error",
    )
    list_filter = (
        "user_account",
        "name",
        "is_sandbox",
        "connected",
    )
    search_fields = (
        "user_account",
        "name",
        "is_sandbox",
    )


admin.site.register(Broker, AdminBroker)
