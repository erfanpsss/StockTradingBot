from email.policy import default
from django.db import models
from data.models import Symbol

BROKERS_LIST = (
    ("FakeBroker", "FakeBroker"),
)
POSITION_TYPES = (
    ("buy", "buy"),
    ("sell", "sell"),
)


class Trade(models.Model):
    TRADE_TYPES_CHOICES = [
        ("open", "open"),
        ("close", "close")
    ]
    id = models.AutoField(primary_key=True)
    trade_type = models.CharField(max_length=10, choices=TRADE_TYPES_CHOICES)
    trade_datetime = models.DateTimeField()
    broker = models.CharField(max_length=20, choices=BROKERS_LIST)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name="trades")
    position_id = models.CharField(max_length=200)
    position_type = models.CharField(max_length=10, choices=POSITION_TYPES)
    trade_price = models.FloatField()
    trade_size = models.FloatField()
    trade_stop_loss = models.FloatField(blank = True, null = True)
    trade_limit = models.FloatField(blank = True, null = True)
    parent_trade = models.ForeignKey("self", on_delete=models.CASCADE, related_name="sub_trades", blank = True, null = True)
    executor = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Trade"
        verbose_name_plural = "Trades"



class BrokerStorage(models.Model):
    id = models.AutoField(primary_key=True)
    broker = models.CharField(max_length=20, choices=BROKERS_LIST)
    storage = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Broker Storage"
        verbose_name_plural = "Broker Storages"