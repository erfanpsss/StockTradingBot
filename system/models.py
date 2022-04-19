from email.policy import default
from django.db import models
from riskmanagement.models import RiskManagement
from trademanagement.models import TradeManagement
from strategy.models import Strategy
from broker.models import Broker
from django.core.management import call_command


def default_symbol_timeframe_pair():
    return [
        {"AAPL": ["1m", "5m"]},
        {"AUDUSD": ["1d", "1h"]},
    ]


class System(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=200)
    is_active = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    broker = models.ForeignKey(
        Broker, on_delete=models.SET_NULL, null=True, blank=True, related_name="system_brokers")
    risk_management = models.ForeignKey(
        RiskManagement, on_delete=models.SET_NULL, null=True, blank=True, related_name="system_risk_managements")
    trade_management = models.ForeignKey(
        TradeManagement, on_delete=models.SET_NULL, null=True, blank=True, related_name="system_trade_managements")
    strategy = models.ForeignKey(
        Strategy, on_delete=models.SET_NULL, null=True, blank=True, related_name="system_strategies")
    symbol_timeframe_pair = models.JSONField(default=dict)
    configurations = models.JSONField(default=dict)
    storage = models.JSONField(default=dict)
    created_on = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "System"
        verbose_name_plural = "Systems"

    def get_data(self):
        for pair in self.symbol_timeframe_pair:
            for symbol, timeframes in pair.items():
                for timeframe in timeframes:
                    call_command("get_data", symbol=symbol,
                                 timeframe=timeframe)
