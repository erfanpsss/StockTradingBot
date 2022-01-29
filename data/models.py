from datetime import datetime
from enum import unique
from pyexpat import model
from tabnanny import verbose
from django.db import models
from django.db.models import Q
import pandas as pd
import math

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
        self.create_ibd_record()

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
        all_ibd_data_obj = []
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
                    "price_change_in_currency": data["Price $ Change"].iloc[counter],
                    "price_change_in_percentage": data["Price % Change"].iloc[counter],
                    "comp_rating": data["Comp. Rating"].iloc[counter],
                    "eps_rating": data["EPS Rating"].iloc[counter],
                    "industry_group_rank": data["Industry Group Rank"].iloc[counter],
                    "rs_rating": data["RS Rating"].iloc[counter],
                    "ind_grp_rs": data["Ind Grp RS"].iloc[counter],
                    "smr_rating": data["SMR Rating"].iloc[counter],
                    "acc_dis_rating": data["Acc/Dis Rating"].iloc[counter],
                    "spon_rating": data["Spon Rating"].iloc[counter],
                    "vol_change_in_percentage": data["Vol. % Change"].iloc[counter],
                    "vol_change_in_1k_s": data["Vol. (1000s)"].iloc[counter],
                }
                all_ibd_data_obj.append(IbdData(**ibd_data_kwargs))
            except Exception as e:
                print(e)
        
        IbdData.objects.bulk_create(all_ibd_data_obj, ignore_conflicts=True)

