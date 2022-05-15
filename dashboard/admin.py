from django.contrib import admin
from .models import Position


class PositionAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        "id",
        "account",
        "status",
        "error",
        "trade_type",
        "order_type",
        "trade_price",
        "trade_datetime",
        "broker",
        "symbol",
        "position_id",
        "position_type",
        "quantity",
        "trade_price",
        "trade_size",
        "trade_stop_loss",
        "trade_limit",
        "executor",
    )
    list_filter = (
        "status",
        "account",
        "trade_type",
        "broker",
        "symbol",
        "parent_trade",
        "executor",

    )
    search_fields = (
        "symbol__name",
        "account",
        "position_id",
        "parent_trade__position_id",
    )

    fields = (
        "account",
        "trade_type",
        "order_type",
        "position_type",
        "symbol",
        "broker",
        "quantity",
        "executor",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Position, PositionAdmin)
