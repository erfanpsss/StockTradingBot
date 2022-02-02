from django.contrib import admin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from .models import Data, Symbol, Timeframe, TimeframeAlias, IbdData, IbdDataFile, FinvizDataFile, FinvizSectorData, FinvizSectorDataFile, Sector
from import_export.admin import ExportActionMixin, ExportMixin
from import_export.fields import Field
from import_export import resources
from django.db.models import F
from django.contrib.admin.views.main import ChangeList
from django.http import HttpResponse
import plotly.express as px


@admin.action(description='Generate scattered chart for given query based on their Price change in percentage field')
def generate_scattered_chart(modeladmin, request, queryset):
    x = list(queryset.values_list("symbol", flat=True))
    y = list(queryset.values_list("price_change_in_percentage", flat = True))
    fig =px.scatter(x=x, y=y, trendline="ols")
    fig.data[1].line.color = 'red'
    chart = fig.to_html()  
    return HttpResponse(chart)

@admin.action(description='Generate line chart for given query based on their Price change in percentage field')
def generate_line_chart(modeladmin, request, queryset):
    x = list(queryset.values_list("date", flat=True))
    y = list(queryset.values_list("price", flat = True))
    fig =px.line(x=x, y=y)
    chart = fig.to_html()  
    return HttpResponse(chart)




@admin.action(description='Generate scattered chart for given query based on their Price change in percentage field')
def generate_sector_scattered_chart(modeladmin, request, queryset):
    x = list(queryset.values_list("sector", flat=True))
    y = list(queryset.values_list("performance_week_percentage", flat = True))
    fig =px.scatter(x=x, y=y, trendline="ols")
    fig.data[1].line.color = 'red'
    chart = fig.to_html()  
    return HttpResponse(chart)

@admin.action(description='Generate line chart for given query based on their Price change in percentage field')
def generate_sector_line_chart(modeladmin, request, queryset):
    x = list(queryset.values_list("date", flat=True))
    y = list(queryset.values_list("performance_week_percentage", flat = True))
    fig =px.line(x=x, y=y)
    chart = fig.to_html()  
    return HttpResponse(chart)

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

class AdminSector(admin.ModelAdmin):
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


class FinvizSectorDataResource(resources.ModelResource):
    class Meta:
        model = FinvizSectorData

    def dehydrate_sector(self, obj):
        return obj.sector.name        


class AdminIbdDataChangeList(ChangeList):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        given_query = request.GET
        fields = IbdData._meta.fields

        given_sort_columns = given_query.get("o") or ""
        if given_sort_columns:
            given_sort_columns = str(given_sort_columns)
            given_sort_columns = given_sort_columns.split(".")
            given_sort_columns = [int(col) for col in given_sort_columns]

        for column in given_sort_columns:
            if column < 0:
                qs = qs.order_by(F(fields[abs(column) - 1].name).desc(nulls_last=True))
            else:
                qs = qs.order_by(F(fields[abs(column) - 1].name).asc(nulls_last=True))
            
        return qs



class AdminIbdData(ExportActionMixin, admin.ModelAdmin):
    list_per_page = 10
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
        "sector",
        "industry",
        "country",
        "earnings_date",
        "ipo_date",
        "symbol",        
    )
    #ordering = ("date", F('price_change_in_percentage').desc(nulls_last=True), "eps_rating", "comp_rating", "industry_group_rank", "rs_rating", "ind_grp_rs", "smr_rating", "acc_dis_rating", "spon_rating",)
    search_fields = (
        "date",
        "symbol__name",
    )

    actions = [generate_scattered_chart, generate_line_chart]


    """
    def get_changelist(self, request, **kwargs):
        return AdminIbdDataChangeList  # PUT YOU OWERRIDEN CHANGE LIST HERE
    """

    def get_rangefilter_created_at_title(self, request, field_path):
        return 'Date range'



class AdminFinvizSectorData(ExportActionMixin, admin.ModelAdmin):
    list_per_page = 10
    list_select_related = ('sector',)
    resource_class = FinvizSectorDataResource
    list_display = (
        "id",
        "sector",
        "date",
        "market_cap",
        "pe",
        "forward_pe",
        "peg",
        "ps",
        "pb",
        "pc",
        "p_free_cash_flow",
        "dividend_yield_percentage",
        "eps_growth_past_5_years_percentage",
        "eps_growth_next_5_years_percentage",
        "sales_growth_past_5_years_percentage",
        "float_short_percentage",
        "performance_week_percentage",
        "performance_month_percentage",
        "performance_quarter_percentage",
        "performance_half_year_percentage",
        "performance_year_percentage",
        "performance_year_to_date_percentage",
        "analyst_recom",
        "average_volume",
        "relative_volume",
        "change_percentage",
        "volume",
        "stocks",
    )
    list_filter = (
        "date",
        ("date", DateRangeFilter),      
    )
    search_fields = (
        "date",
        "sector__name",
    )

    actions = [generate_sector_scattered_chart, generate_sector_line_chart]
    

    """
    def get_changelist(self, request, **kwargs):
        return AdminIbdDataChangeList  # PUT YOU OWERRIDEN CHANGE LIST HERE
    """

    def get_rangefilter_created_at_title(self, request, field_path):
        return 'Date range'











class AdminIbdDataFile(admin.ModelAdmin):
    list_display = (
        "id",
        "created_date",
        "data_date",
        "file",
        "is_processed",
        "is_processing",
        "processed_date",
        "errors",
    )
    list_filter = (
        "id",
        "created_date",
        "data_date",
        "is_processed", 
        "is_processing",
        "processed_date",
    )
    ordering = ("created_date",)
    search_fields = (
        "id",
        "file",
        "created_date",
        "data_date",
        "is_processed",
        "is_processing",
        "processed_date",
    )


class AdminFinvizDataFile(admin.ModelAdmin):
    list_display = (
        "id",
        "creator",
        "created_date",
        "data_date",
        "file",
        "is_processed",
        "is_processing",
        "processed_date",
        "errors",        
    )
    list_filter = (
        "id",
        "creator",
        "created_date",
        "data_date",
        "is_processed",
        "is_processing",
        "processed_date",
    )
    ordering = ("created_date",)
    search_fields = (
        "id",
        "creator",
        "file",
        "created_date",
        "data_date",
        "is_processed",
        "is_processing",
        "processed_date",
    )



class AdminFinvizSectorDataFile(admin.ModelAdmin):
    list_display = (
        "id",
        "creator",
        "created_date",
        "data_date",
        "file",
        "is_processed",
        "is_processing",
        "processed_date",
        "errors",        
    )
    list_filter = (
        "id",
        "creator",
        "created_date",
        "data_date",
        "is_processed",
        "is_processing",
        "processed_date",
    )
    ordering = ("created_date",)
    search_fields = (
        "id",
        "creator",
        "file",
        "created_date",
        "data_date",
        "is_processed",
        "is_processing",
        "processed_date",
    )




admin.site.register(TimeframeAlias, AdminTimeframeAlias)
admin.site.register(Timeframe, AdminTimeframe)
admin.site.register(Symbol, AdminSymbol)
admin.site.register(Sector, AdminSector)
admin.site.register(Data, AdminData)
admin.site.register(IbdData, AdminIbdData)
admin.site.register(IbdDataFile, AdminIbdDataFile)
admin.site.register(FinvizDataFile, AdminFinvizDataFile)
admin.site.register(FinvizSectorData, AdminFinvizSectorData)
admin.site.register(FinvizSectorDataFile, AdminFinvizSectorDataFile)