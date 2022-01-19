from django.contrib import admin

from .models import Data, Symbol, Timeframe, TimeframeAlias


class AdminTimeframeAlias(admin.ModelAdmin):
    list_display = ("name",)
    ordeing = ("name",)
    search_fields = ("name",)


class AdminTimeframe(admin.ModelAdmin):
    list_display = ("name",)
    ordeing = ("name",)
    search_fields = ("name",)


class AdminSymbol(admin.ModelAdmin):
    list_display = ("name",)
    ordeing = ("name",)
    search_fields = ("name",)


class AdminData(admin.ModelAdmin):
    list_display = (
        "symbol",
        "timeframe",
        "datetime",
    )
    list_filter = (
        "symbol",
        "timeframe",
        "datetime",
    )
    ordeing = ("datetime",)
    search_fields = (
        "datetime",
    )


admin.site.register(TimeframeAlias, AdminTimeframeAlias)
admin.site.register(Timeframe, AdminTimeframe)
admin.site.register(Symbol, AdminSymbol)
admin.site.register(Data, AdminData)
