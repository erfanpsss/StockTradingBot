from django.db import models
from django.db.models import Q

class Symbol(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Sybmol"
        verbose_name_plural = "Sybmols"

    def __str__(self):
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
