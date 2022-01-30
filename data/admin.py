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
        "dividend_yield_percentage",
        "payout_ratio_percentage",
        "eps_ttm",
        "eps_growth_this_year_percentage",
        "eps_growth_next_year_percentage",
        "eps_growth_past_5_years_percentage",
        "eps_growth_next_5_years_percentage",
        "sales_growth_past_5_years_percentage",
        "eps_growth_quarter_over_quarter_percentage",
        "sales_growth_quarter_over_quarter_percentage",
        "shares_outstanding",
        "share_float",
        "insider_ownership_percentage",
        "insider_transactions_percentage",
        "institutional_ownership_percentage",
        "institutional_transactions_percentage",
        "float_short_percentage",
        "short_ratio",
        "return_on_assets_percentage",
        "return_on_equity_percentage",
        "return_on_investment_percentage",
        "current_ratio",
        "quick_ratio",
        "lt_debt_equity",
        "total_debt_equity",
        "gross_margin_percentage",
        "operating_margin_percentage",
        "profit_margin_percentage",
        "performance_week_percentage",
        "performance_month_percentage",
        "performance_quarter_percentage",
        "performance_half_year_percentage",
        "performance_year_percentage",
        "performance_ytd_percentage",
        "beta",
        "average_true_range",
        "volatility_week_percentage",
        "volatility_month_percentage",
        "simple_moving_average_20_day_percentage",
        "simple_moving_average_50_day_percentage",
        "simple_moving_average_200_day_percentage",
        "high_50_day_percentage",
        "low_50_day_percentage",
        "high_52_week_percentage",
        "low_52_week_percentage",
        "relative_strength_index_14",
        "change_from_open_percentage",
        "gap_percentage",
        "analyst_recom",
        "average_volume",
        "relative_volume",
        "finviz_price",
        "change_percentage",
        "volume",
        "earnings_date",
        "target_price",
        "ipo_date",
        "after_hours_close",
        "after_hours_change_percentage",
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
        "is_processed",
        "processed_date",
        "errors",
    )
    list_filter = (
        "id",
        "created_date",
        "is_processed", 
        "processed_date",
    )
    ordering = ("created_date",)
    search_fields = (
        "id",
        "file",
        "created_date",
        "is_processed",
        "processed_date",
    )


class AdminFinvizDataFile(admin.ModelAdmin):
    list_display = (
        "id",
        "created_date",
        "file",
        "is_processed",
        "processed_date",
        "errors",        
    )
    list_filter = (
        "id",
        "created_date",
        "is_processed",
        "processed_date",
    )
    ordering = ("created_date",)
    search_fields = (
        "id",
        "file",
        "created_date",
        "is_processed",
        "processed_date",
    )








admin.site.register(TimeframeAlias, AdminTimeframeAlias)
admin.site.register(Timeframe, AdminTimeframe)
admin.site.register(Symbol, AdminSymbol)
admin.site.register(Data, AdminData)
admin.site.register(IbdData, AdminIbdData)
admin.site.register(IbdDataFile, AdminIbdDataFile)
admin.site.register(FinvizDataFile, AdminFinvizDataFile)