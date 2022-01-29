from django.contrib import admin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from .models import Data, Symbol, Timeframe, TimeframeAlias, IbdData, IbdDataFile, FinvizDataFile
from import_export.admin import ExportActionMixin, ExportMixin
from import_export.fields import Field
from import_export import resources

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



class IbdDataResource(resources.ModelResource):
    class Meta:
        model = IbdData

    def dehydrate_symbol(self, obj):
        return obj.symbol.name

class AdminIbdData(ExportActionMixin, admin.ModelAdmin):
    list_per_page = 15
    list_select_related = ('symbol',)
    resource_class = IbdDataResource
    list_display = (
        "id",
        "symbol",
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
        "company",
        "sector",
        "industry",
        "country",
        "market_cap",
        "pe",
        "forward_pe",
        "peg",
        "ps",
        "pb",
        "p_cash",
        "p_free_cash_flow",
        "dividend_yield",
        "payout_ratio",
        "eps_ttm",
        "eps_growth_this_year",
        "eps_growth_next_year",
        "eps_growth_past_5_years",
        "eps_growth_next_5_years",
        "sales_growth_past_5_years",
        "eps_growth_quarter_over_quarter",
        "sales_growth_quarter_over_quarter",
        "shares_outstanding",
        "share_float",
        "insider_ownership",
        "insider_transactions",
        "institutional_ownership",
        "institutional_transactions",
        "float_short",
        "short_ratio",
        "return_on_assets",
        "return_on_equity",
        "return_on_investment",
        "current_ratio",
        "quick_ratio",
        "lt_debt_equity",
        "total_debt_equity",
        "gross_margin",
        "operating_margin",
        "profit_margin",
        "performance_week",
        "performance_month",
        "performance_quarter",
        "performance_half_year",
        "performance_year",
        "performance_ytd",
        "beta",
        "average_true_range",
        "volatility_week",
        "volatility_month",
        "simple_moving_average_20_day",
        "simple_moving_average_50_day",
        "simple_moving_average_200_day",
        "high_50_day",
        "low_50_day",
        "high_52_week",
        "low_52_week",
        "relative_strength_index_14",
        "change_from_open",
        "gap",
        "analyst_recom",
        "average_volume",
        "relative_volume",
        "finviz_price",
        "change",
        "volume",
        "earnings_date",
        "target_price",
        "ipo_date",
        "after_hours_close",
        "after_hours_change",
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
    ordering = ("date", "eps_rating", "comp_rating", "industry_group_rank", "rs_rating", "ind_grp_rs", "smr_rating", "acc_dis_rating", "spon_rating",)
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
    ordering = ("created_date",)
    search_fields = (
        "id",
        "file",
        "created_date",
    )


class AdminFinvizDataFile(admin.ModelAdmin):
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
    ordering = ("created_date",)
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
admin.site.register(FinvizDataFile, AdminFinvizDataFile)