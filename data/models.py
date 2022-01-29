from datetime import datetime
from enum import unique
from pyexpat import model
from tabnanny import verbose
from django.db import models
from django.db.models import Q
import pandas as pd
import math
import threading

FINVIZ_DATE_FORMAT = "%m/%d/%Y"
FINVIZ_DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S %p"

class Symbol(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique = True)

    class Meta:
        verbose_name = "Sybmol"
        verbose_name_plural = "Sybmols"

    def __str__(self):
        return self.name.upper()

    def __unicode__(self):
        return self.name.upper()

class TimeframeAlias(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name = "Timeframe alias"
        verbose_name_plural = "Timeframe aliases"

    def __str__(self):
        return self.name.upper()

class Timeframe(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)
    alias_id = models.ManyToManyField(
        TimeframeAlias, related_name="timeframe_other_name"
    )

    class Meta:
        verbose_name = "Timeframe"
        verbose_name_plural = "Timeframes"

    def __str__(self):
        return self.name

class Data(models.Model):
    id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField()
    timeframe = models.ForeignKey(Timeframe, on_delete=models.CASCADE, related_name = "data_timeframe")
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name = "data_symbol")
    open_bid = models.FloatField()
    close_bid = models.FloatField()
    high_bid = models.FloatField()
    low_bid = models.FloatField()
    open_ask = models.FloatField(blank = True, null = True)
    close_ask = models.FloatField(blank = True, null = True)
    high_ask = models.FloatField(blank = True, null = True)
    low_ask = models.FloatField(blank = True, null = True)
    volume = models.FloatField(blank = True, null = True)
        
    class Meta:
        unique_together = ("datetime", "timeframe", "symbol")
        verbose_name = "Data"
        verbose_name_plural = "Data"


    @property
    def price(self):
        if self.timeframe.name == "t1":
            return self.price_bid
        return self.close_bid

    @property
    def is_tick(self):
        return self.timeframe.name == "t1"

    @property
    def previous_value(self):

        value = (
            self.__class__.objects.filter(
                Q(symbol=self.symbol) & Q(timeframe=self.timeframe)
            )
            .filter(datetime__lt=self.datetime)
            .order_by("datetime")
            .last()
        )
        return value.price if value else None

    @classmethod
    def get_available_indicator_configuration(cls):
        #from risk_management.models import RISK_MANAGEMENT
        from strategy.models import Strategy
        indicators_configurations_all = []

        # Available indicators and configuration format
        # AVAILABLE_INDICATORS = [
        #    {"class": "MOVING_AVERAGE", "args": {"period": 10}},
        #    {"class": "EXPONENTIAL_MOVING_AVERAGE", "args": {"period": 10}},
        # ]

        indicators_configurations_all += list(
            Strategy.objects.filter(active=True).values_list(
                "indicators_configuration", flat=True
            )
        )
        #indicators_configurations_all += list(
        #    RISK_MANAGEMENT.objects.filter(active=True).values_list(
        #        "indicators_configuration", flat=True
        #    )
        #)
        indicators_configurations = []
        for indicator_configuration in indicators_configurations_all:
            for conf in indicator_configuration:
                if conf not in indicators_configurations:
                    indicators_configurations.append(conf)
        return indicators_configurations





class IbdData(models.Model):
    id = models.AutoField(primary_key=True)

    # IBD data
    date = models.DateField()
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name="ibd_data")
    price = models.FloatField()
    price_change_in_currency = models.FloatField()
    price_change_in_percentage = models.FloatField()
    comp_rating = models.FloatField(blank = True, null = True)
    eps_rating = models.FloatField(blank = True, null = True)
    industry_group_rank = models.FloatField(blank = True, null = True)
    rs_rating = models.FloatField(blank = True, null = True)
    ind_grp_rs = models.CharField(max_length=10)
    smr_rating = models.CharField(max_length=10)
    acc_dis_rating = models.CharField(max_length=10)
    spon_rating = models.CharField(max_length=10)
    vol_change_in_percentage = models.FloatField(blank = True, null = True)
    vol_change_in_1k_s = models.FloatField(blank = True, null = True)
    
    # Finviz data
    company=models.CharField(max_length = 255, blank = True, null = True)
    sector=models.CharField(max_length = 255, blank = True, null = True)
    industry=models.CharField(max_length = 255, blank = True, null = True)
    country=models.CharField(max_length = 255, blank = True, null = True)
    market_cap=models.FloatField(blank = True, null = True)
    pe=models.FloatField(blank = True, null = True)
    forward_pe=models.FloatField(blank = True, null = True)
    peg=models.FloatField(blank = True, null = True)
    ps=models.FloatField(blank = True, null = True)
    pb=models.FloatField(blank = True, null = True)
    p_cash=models.FloatField(blank = True, null = True)
    p_free_cash_flow=models.FloatField(blank = True, null = True)
    dividend_yield_percentage=models.FloatField(blank = True, null = True)
    payout_ratio_percentage=models.FloatField(blank = True, null = True)
    eps_ttm=models.FloatField(blank = True, null = True)
    eps_growth_this_year_percentage=models.FloatField(blank = True, null = True)
    eps_growth_next_year_percentage=models.FloatField(blank = True, null = True)
    eps_growth_past_5_years_percentage=models.FloatField(blank = True, null = True)
    eps_growth_next_5_years_percentage=models.FloatField(blank = True, null = True)
    sales_growth_past_5_years_percentage=models.FloatField(blank = True, null = True)
    eps_growth_quarter_over_quarter_percentage=models.FloatField(blank = True, null = True)
    sales_growth_quarter_over_quarter_percentage=models.FloatField(blank = True, null = True)
    shares_outstanding=models.FloatField(blank = True, null = True)
    share_float=models.FloatField(blank = True, null = True)
    insider_ownership_percentage=models.FloatField(blank = True, null = True)
    insider_transactions_percentage=models.FloatField(blank = True, null = True)
    institutional_ownership_percentage=models.FloatField(blank = True, null = True)
    institutional_transactions_percentage=models.FloatField(blank = True, null = True)
    float_short_percentage=models.FloatField(blank = True, null = True)
    short_ratio=models.FloatField(blank = True, null = True)
    return_on_assets_percentage=models.FloatField(blank = True, null = True)
    return_on_equity_percentage=models.FloatField(blank = True, null = True)
    return_on_investment_percentage=models.FloatField(blank = True, null = True)
    current_ratio=models.FloatField(blank = True, null = True)
    quick_ratio=models.FloatField(blank = True, null = True)
    lt_debt_equity=models.FloatField(blank = True, null = True)
    total_debt_equity=models.FloatField(blank = True, null = True)
    gross_margin_percentage=models.FloatField(blank = True, null = True)
    operating_margin_percentage=models.FloatField(blank = True, null = True)
    profit_margin_percentage=models.FloatField(blank = True, null = True)
    performance_week_percentage=models.FloatField(blank = True, null = True)
    performance_month_percentage=models.FloatField(blank = True, null = True)
    performance_quarter_percentage=models.FloatField(blank = True, null = True)
    performance_half_year_percentage=models.FloatField(blank = True, null = True)
    performance_year_percentage=models.FloatField(blank = True, null = True)
    performance_ytd_percentage=models.FloatField(blank = True, null = True)
    beta=models.FloatField(blank = True, null = True)
    average_true_range=models.FloatField(blank = True, null = True)
    volatility_week_percentage=models.FloatField(blank = True, null = True)
    volatility_month_percentage=models.FloatField(blank = True, null = True)
    simple_moving_average_20_day_percentage=models.FloatField(blank = True, null = True)
    simple_moving_average_50_day_percentage=models.FloatField(blank = True, null = True)
    simple_moving_average_200_day_percentage=models.CharField(max_length = 255, blank = True, null = True)
    high_50_day_percentage=models.FloatField(blank = True, null = True)
    low_50_day_percentage=models.FloatField(blank = True, null = True)
    high_52_week_percentage=models.FloatField(blank = True, null = True)
    low_52_week_percentage=models.FloatField(blank = True, null = True)
    relative_strength_index_14=models.FloatField(blank = True, null = True)
    change_from_open_percentage=models.FloatField(blank = True, null = True)
    gap_percentage=models.FloatField(blank = True, null = True)
    analyst_recom=models.FloatField(blank = True, null = True)
    average_volume=models.FloatField(blank = True, null = True)
    relative_volume=models.FloatField(blank = True, null = True)
    finviz_price=models.FloatField(blank = True, null = True)
    change_percentage=models.FloatField(blank = True, null = True)
    volume=models.FloatField(blank = True, null = True)
    earnings_date=models.DateTimeField(blank = True, null = True)
    target_price=models.FloatField(blank = True, null = True)
    ipo_date=models.DateField(blank = True, null = True)
    after_hours_close=models.FloatField(blank = True, null = True)
    after_hours_change_percentage=models.FloatField(blank = True, null = True)

    class Meta:
        unique_together = ("date", "symbol")
        verbose_name = "IBD data"
        verbose_name_plural = "IBD data"


class IbdDataFile(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to="ibd_data_files")
    created_date = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "IBD data file"
        verbose_name_plural = "IBD data files"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        thread = threading.Thread(target=self.create_ibd_record, args=())
        thread.start()

    def prepare_data(self):
        data=pd.read_excel(self.file.file, skiprows=[0,1,2,3])
        record_datetime = data.iloc[0][1]
        record_datetime=[d.strip() for d in record_datetime.split(",")[-2:]] 
        record_datetime = datetime.strptime(" ".join(record_datetime), "%B %d %Y") 
        record_datetime = record_datetime.date()
        data=pd.read_excel(self.file.file, skiprows=[0,1,2,3,4,5,6,7,8])
        return data, record_datetime

    def create_ibd_record(self):
        data, record_datetime=self.prepare_data()
        for counter, index in enumerate(data.index):
            try:
                symbol_temp = data["Symbol"].iloc[counter]
                if isinstance(symbol_temp, float) and math.isnan(symbol_temp):
                    break
                symbol_obj, created = Symbol.objects.get_or_create(name = symbol_temp)
                ibd_data_kwargs = {
                    "date": record_datetime,
                    "symbol": symbol_obj,
                    "price": data["Price"].iloc[counter],
                    "price_change_in_currency": data["Price $ Change_percentage"].iloc[counter],
                    "price_change_in_percentage": data["Price % Change_percentage"].iloc[counter],
                    "comp_rating": data["Comp. Rating"].iloc[counter],
                    "eps_rating": data["EPS Rating"].iloc[counter],
                    "industry_group_rank": data["Industry Group Rank"].iloc[counter],
                    "rs_rating": data["RS Rating"].iloc[counter],
                    "ind_grp_rs": data["Ind Grp RS"].iloc[counter],
                    "smr_rating": data["SMR Rating"].iloc[counter],
                    "acc_dis_rating": data["Acc/Dis Rating"].iloc[counter],
                    "spon_rating": data["Spon Rating"].iloc[counter],
                    "vol_change_in_percentage": data["Vol. % Change_percentage"].iloc[counter],
                    "vol_change_in_1k_s": data["Vol. (1000s)"].iloc[counter],
                }
                IbdData.objects.update_or_create(**ibd_data_kwargs)
            except Exception as e:
                print(e)
        


class FinvizDataFile(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to="finviz_data_files")
    created_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Finviz data file"
        verbose_name_plural = "Finviz data files"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        thread = threading.Thread(target=self.create_finviz_record, args=())
        thread.start()

    def prepare_data(self):
        data=pd.read_excel(self.file.file)
        date_fields = ["IPO Date"]
        datetime_fields = ["Earnings Date"]
        percentage_fields = [
            "Dividend Yield", 
            "Payout Ratio", 
            "EPS growth this year", 
            "EPS growth next year", 
            "EPS growth past 5 years", 
            "EPS growth next 5 years", 
            "Sales growth past 5 years",
            "EPS growth quarter over quarter",
            "Sales growth quarter over quarter",
            "Insider Ownership",
            "Insider Transactions",
            "Institutional Ownership",
            "Institutional Transactions",
            "Float Short",
            "Return on Assets",
            "Return on Equity",
            "Return on Investment",
            "Gross Margin",
            "Operating Margin",
            "Profit Margin",
            "Performance (Week)",
            "Performance (Month)",
            "Performance (Quarter)",
            "Performance (Half Year)",
            "Performance (Year)",
            "Performance (YTD)",
            "Volatility (Week)",
            "Volatility (Month)",
            "20-Day Simple Moving Average",
            "50-Day Simple Moving Average",
            "200-Day Simple Moving Average",
            "50-Day High",
            "50-Day Low",
            "52-Week High",
            "52-Week Low",
            "Change from Open",
            "Gap",
            "Change",
            "After-Hours Change",
        ]
        for counter, index in enumerate(data.index):
            for date_field in date_fields:
                data[date_field].iloc[counter] = datetime.strptime(data[date_field].iloc[counter], FINVIZ_DATE_FORMAT)
            for datetime_field in datetime_fields:
                data[datetime_field].iloc[counter] = datetime.strptime(data[datetime_field].iloc[counter], FINVIZ_DATETIME_FORMAT)
            for percentage_field in percentage_fields:
                if data[percentage_field].iloc[counter]:
                    data[percentage_field].iloc[counter] = float(data[percentage_field].iloc[counter].replace("%", "").stript())

        record_datetime = datetime.utcnow().date()
        return data, record_datetime

    def create_finviz_record(self):
        data, record_datetime=self.prepare_data()
        for counter, index in enumerate(data.index):
            try:
                symbol_temp = data["Symbol"].iloc[counter]
                symbol_obj, created = Symbol.objects.get_or_create(name = symbol_temp)
                ibd_data_kwargs = {
                    "date": record_datetime,
                    "symbol": symbol_obj,
                    # from hero ...
                    "company": data["Company"].iloc[counter],
                    "sector": data["Sector"].iloc[counter],
                    "industry": data["Industry"].iloc[counter],
                    "country": data["Country"].iloc[counter],
                    "market_cap": data["Market Cap"].iloc[counter],
                    "pe": data["P/E"].iloc[counter],
                    "forward_pe": data["Forward P/E"].iloc[counter],
                    "peg": data["PEG"].iloc[counter],
                    "ps": data["P/S"].iloc[counter],
                    "pb": data["P/B"].iloc[counter],
                    "p_cash": data["P/Cash"].iloc[counter],
                    "p_free_cash_flow": data["P/Free Cash Flow"].iloc[counter],
                    "dividend_yield_percentage": data["Dividend Yield"].iloc[counter],
                    "payout_ratio_percentage": data["Payout Ratio"].iloc[counter],
                    "eps_ttm": data["EPS (ttm)"].iloc[counter],
                    "eps_growth_this_year_percentage": data["EPS growth this year"].iloc[counter],
                    "eps_growth_next_year_percentage": data["EPS growth next year"].iloc[counter],
                    "eps_growth_past_5_years_percentage": data["EPS growth past 5 years"].iloc[counter],
                    "eps_growth_next_5_years_percentage": data["EPS growth next 5 years"].iloc[counter],
                    "sales_growth_past_5_years_percentage": data["Sales growth past 5 years"].iloc[counter],
                    "eps_growth_quarter_over_quarter_percentage": data["EPS growth quarter over quarter"].iloc[counter],
                    "sales_growth_quarter_over_quarter_percentage": data["Sales growth quarter over quarter"].iloc[counter],
                    "shares_outstanding": data["Shares Outstanding"].iloc[counter],
                    "share_float": data["Shares Float"].iloc[counter],
                    "insider_ownership_percentage": data["Insider Ownership"].iloc[counter],
                    "insider_transactions_percentage": data["Insider Transactions"].iloc[counter],
                    "institutional_ownership_percentage": data["Institutional Ownership"].iloc[counter],
                    "institutional_transactions_percentage": data["Institutional Transactions"].iloc[counter],
                    "float_short_percentage": data["Float Short"].iloc[counter],
                    "short_ratio": data["Short Ratio"].iloc[counter],
                    "return_on_assets_percentage": data["Return on Assets"].iloc[counter],
                    "return_on_equity_percentage": data["Return on Equity"].iloc[counter],
                    "return_on_investment_percentage": data["Return on Investment"].iloc[counter],
                    "current_ratio": data["Current Ratio"].iloc[counter],
                    "quick_ratio": data["Quick Ratio"].iloc[counter],
                    "lt_debt_equity": data["LT Debt/Equity"].iloc[counter],
                    "total_debt_equity": data["Total Debt/Equity"].iloc[counter],
                    "gross_margin_percentage": data["Gross Margin"].iloc[counter],
                    "operating_margin_percentage": data["Operating Margin"].iloc[counter],
                    "profit_margin_percentage": data["Profit Margin"].iloc[counter],
                    "performance_week_percentage": data["Performance (Week)"].iloc[counter],
                    "performance_month_percentage": data["Performance (Month)"].iloc[counter],
                    "performance_quarter_percentage": data["Performance (Quarter)"].iloc[counter],
                    "performance_half_year_percentage": data["Performance (Half Year)"].iloc[counter],
                    "performance_year_percentage": data["Performance (Year)"].iloc[counter],
                    "performance_ytd_percentage": data["Performance (YTD)"].iloc[counter],
                    "beta": data["Beta"].iloc[counter],
                    "average_true_range": data["Average True Range"].iloc[counter],
                    "volatility_week_percentage": data["Volatility (Week)"].iloc[counter],
                    "volatility_month_percentage": data["Volatility (Month)"].iloc[counter],
                    "simple_moving_average_20_day_percentage": data["20-Day Simple Moving Average"].iloc[counter],
                    "simple_moving_average_50_day_percentage": data["50-Day Simple Moving Average"].iloc[counter],
                    "simple_moving_average_200_day_percentage": data["200-Day Simple Moving Average"].iloc[counter],
                    "high_50_day_percentage": data["50-Day High"].iloc[counter],
                    "low_50_day_percentage": data["50-Day Low"].iloc[counter],
                    "high_52_week_percentage": data["52-Week High"].iloc[counter],
                    "low_52_week_percentage": data["52-Week Low"].iloc[counter],
                    "relative_strength_index_14": data["Relative Strength Index (14)"].iloc[counter],
                    "change_from_open_percentage": data["Change_percentage from Open"].iloc[counter],
                    "gap_percentage": data["Gap_percentage"].iloc[counter],
                    "analyst_recom": data["Analyst Recom"].iloc[counter],
                    "average_volume": data["Average Volume"].iloc[counter],
                    "relative_volume": data["Relative Volume"].iloc[counter],
                    "finviz_price": data["Price"].iloc[counter],
                    "change_percentage": data["Change_percentage"].iloc[counter],
                    "volume": data["Volume"].iloc[counter],
                    "earnings_date": data["Earnings Date"].iloc[counter],
                    "target_price": data["Target Price"].iloc[counter],
                    "ipo_date": data["IPO Date"].iloc[counter],
                    "after_hours_close": data["After-Hours Close"].iloc[counter],
                    "after_hours_change_percentage": data["After-Hours Change_percentage"].iloc[counter],

                }
                IbdData.objects.update_or_create(**ibd_data_kwargs)
            except Exception as e:
                print(e)
