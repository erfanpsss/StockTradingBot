from django.contrib import admin

from .models import TradeManagement


class AdminTradeManagement(admin.ModelAdmin):
    pass


admin.site.register(TradeManagement, AdminTradeManagement)
