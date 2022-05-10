from email.policy import default
from django.db import models
from account.models import Account
from riskmanagement.models import RiskManagement
from trademanagement.models import TradeManagement
from strategy.models import Strategy
from broker.models import Broker
from django.core.management import call_command
from data.models import Timeframe


def default_symbol_timeframe_pair():
    return [
        {"AAPL": ["1m", "5m"]},
        {"AUDUSD": ["1d", "1h"]},
    ]


class System(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=200)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="account_systems")

    is_active = models.BooleanField(default=False)
    is_active_manual_trade_handling = models.BooleanField(default=True)
    is_active_automatic_trade_handling = models.BooleanField(default=True)
    base_timeframe = models.ForeignKey(
        Timeframe, on_delete=models.SET_NULL, null=True, blank=True, related_name="system_timeframes")
    description = models.TextField(null=True, blank=True)
    broker = models.ForeignKey(
        Broker, on_delete=models.SET_NULL, null=True, blank=True, related_name="system_brokers")
    risk_management = models.ForeignKey(
        RiskManagement, on_delete=models.SET_NULL, null=True, blank=True, related_name="system_risk_managements")
    trade_management = models.ForeignKey(
        TradeManagement, on_delete=models.SET_NULL, null=True, blank=True, related_name="system_trade_managements")
    strategy = models.ForeignKey(
        Strategy, on_delete=models.SET_NULL, null=True, blank=True, related_name="system_strategies")

    symbol_timeframe_pair = models.JSONField(
        null=True, blank=True, default=dict)
    configurations = models.JSONField(null=True, blank=True, default=dict)
    storage = models.JSONField(null=True, blank=True, default=dict)
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

    def add_symbol_timeframe_pair(self, symbol, timeframe):
        is_found = False
        current_symbol_timeframe_pairs = self.symbol_timeframe_pair
        for counter, pair in enumerate(current_symbol_timeframe_pairs):
            if list(pair.key())[0] == symbol and timeframe in list(pair.values())[0]:
                is_found = True
                break
            if list(pair.key())[0] == symbol and timeframe not in list(pair.values())[0]:
                current_symbol_timeframe_pairs[counter][symbol].append(
                    timeframe)
                is_found = True
                break
        if not is_found:
            current_symbol_timeframe_pairs.append({symbol: [timeframe]})
        self.symbol_timeframe_pair = current_symbol_timeframe_pairs
        self.save(update_fields="symbol_timeframe_pair")

    def remove_symbol_timeframe_pair(self, symbol, timeframe):
        is_found = False
        current_symbol_timeframe_pairs = self.symbol_timeframe_pair
        for counter, pair in enumerate(current_symbol_timeframe_pairs):
            if list(pair.key())[0] == symbol and timeframe in list(pair.values())[0]:
                is_found = True
                del current_symbol_timeframe_pairs[counter]
                break
        if is_found:
            self.symbol_timeframe_pair = current_symbol_timeframe_pairs
            self.save(update_fields="symbol_timeframe_pair")

    def handle_manual_trades(self):
        trades = self.system_trades.filter(
            is_executed=False)
        for trade in trades:
            current_symbol_timeframe_pair = self.symbol_timeframe_pair
            current_symbol_timeframe_pair.append(
                {trade.symbol.name: [self.base_timeframe.name]})
            self.symbol_timeframe_pair = current_symbol_timeframe_pair
            self.save(update_fields="symbol_timeframe_pair")

    def run(self):
        self.get_data()
        self.trade_management.run(self)
