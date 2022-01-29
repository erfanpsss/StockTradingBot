from django.contrib import admin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from .models import Data, Symbol, Timeframe, TimeframeAlias, IbdData, IbdDataFile


class AdminTimeframeAlias(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name",)
    search_fields = ("name",)


class AdminTimeframe(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name",)
    search_fields = ("name",)


class AdminSymbol(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name",)
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
    ordering = ("datetime",)
    search_fields = (
        "datetime",
    )



class AdminIbdData(admin.ModelAdmin):
    list_per_page = 15
    list_select_related = ('symbol',)
    list_display = (
        "id",
        "symbol_name",
        "date",
        "price",
        "price_change_in_currency",
        "price_change_in_percentage",
        "comp_rating",
        "eps_rating",
        "industry_group_rank",
        "rs_rating",
        "ind_grp_rs",
        "smr_rating",
        "acc_dis_rating",
        "spon_rating",
        "vol_change_in_percentage",
        "vol_change_in_1k_s",
    )
    list_filter = (
        "date",
        ("date", DateRangeFilter),
        "ind_grp_rs",
        "smr_rating",
        "acc_dis_rating",
        "spon_rating",
        "symbol",
    )
    ordering = ("date", "-eps_rating", "-comp_rating", "industry_group_rank", "rs_rating", "ind_grp_rs", "smr_rating", "acc_dis_rating", "spon_rating",)
    search_fields = (
        "date",
        "symbol__name",
    )

    def get_rangefilter_created_at_title(self, request, field_path):
        return 'Date range'


class AdminIbdDataFile(admin.ModelAdmin):
    list_display = (
        "id",
        "created_date",
        "file",
    )
    list_filter = (
        "id",
        "created_date",
        "file",
    )
    ordeing = ("created_date",)
    search_fields = (
        "id",
        "file",
        "created_date",
    )










admin.site.register(TimeframeAlias, AdminTimeframeAlias)
admin.site.register(Timeframe, AdminTimeframe)
admin.site.register(Symbol, AdminSymbol)
admin.site.register(Data, AdminData)
admin.site.register(IbdData, AdminIbdData)
admin.site.register(IbdDataFile, AdminIbdDataFile)
