from django.contrib import admin
from .models import Trade


@admin.action(description='Close position completely or cancel pending order')
def total_close_position(modeladmin, request, queryset):
    for position in queryset:
        Trade.close_position(position, total = True)

class AdminTrade(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        "id",
        "status",
        "error",
        "trade_type",
        "order_type",
        "trade_price",
        "trade_datetime",
        "broker",
        "symbol",
        "position_id",
        "parent_trade_position_id",
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
        "trade_type",
        "broker",
        "symbol",
        "parent_trade",
        "executor",
        
    )
    search_fields = (
        "symbol__name",
        "position_id",
        "parent_trade__position_id",
    )


    fields = (
        "place_now",
        "trade_type",
        "order_type",
        "position_type",
        "symbol",
        "broker",
        "quantity",
        "trade_price",
        "executor",
        "parent_trade",
        "status",
        "trade_datetime",
        "position_id",
        "sent_arguments",
        "error",
    )


    actions = [total_close_position]



admin.site.register(Trade, AdminTrade)