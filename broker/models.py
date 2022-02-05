from email.policy import default
from django.db import models
from data.models import Symbol
import importlib
from django.contrib.auth.models import User
import datetime
import uuid

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




class Broker(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_broker")
    name = models.CharField(max_length=50)
    is_sandbox = models.BooleanField(default=True)
    public_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    broker_class = models.CharField(max_length=50, choices=BROKERS_LIST)
    storage = models.JSONField(default=dict)
    balance = models.FloatField(default=0.0)
    equity = models.FloatField(default=0.0)
    used_maring = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "Broker"
        verbose_name_plural = "Brokers"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.broker_class:
            self.setup()

    def setup(self):
        broker_main_module = importlib.import_module("broker.brokers")
        broker_class = getattr(broker_main_module, self.broker_class)
        self.broker = broker_class(self.is_sandbox, self.public_key, self.secret_key)

    def connection_test(self):
        try:
            return self.broker.connect()
        except Exception as e:
            return str(e)

    def refresh_account_info(self):
        try:
            account_info = self.broker.account_info
            self.balance = account_info.get("balance")
            self.equity = account_info.get("equity")
            self.used_margin = account_info.get("used_margin")
            self.save()
        except Exception as e:
            return str(e)

    @property
    def account_info(self):
        return f"Balance: {self.balance}, equity: {self.equity}, used margin: {self.used_margin}"

    def open_position(self, *args, **kwargs):
        try:
            transaction_id = self.broker.open_position(*args, **kwargs)
            position_size: float = kwargs.get("position_size")
            position_stop_loss: float = kwargs.get("stop_loss")
            position_limit: float = kwargs.get("limit")
            symbol: Symbol = kwargs.get("symbol")
            position_type: str = kwargs.get("position_type")
            trade_datetime: datetime.datetime = kwargs.get("trade_datetime")
            trade_price = datetime.datetime = kwargs.get("trade_price")
            executor: str = kwargs.get("executor")
            trade_type: str = "open"
            broker: str = "FakeBroker"

            data: dict = {
                "position_size": position_size,
                "position_stop_loss": position_stop_loss,
                "position_limit": position_limit,
                "symbol": symbol,
                "position_type": position_type,
                "trade_datetime": trade_datetime,
                "trade_price": trade_price,
                "trade_type": trade_type,
                "position_id": transaction_id,
                "broker": broker,
                "executor": executor
            }

            trade: Trade = Trade.objects.create(**data)
            return trade.pk

        except Exception as e:
            return str(e)

    def close_position(self, *args, **kwargs):
        try:
            transaction_id = self.broker.close_position(*args, **kwargs)
            position_size: float = kwargs.get("position_size")
            position_stop_loss: float = kwargs.get("stop_loss")
            position_limit: float = kwargs.get("limit")
            symbol: Symbol = kwargs.get("symbol")
            position_type: str = kwargs.get("position_type")
            trade_datetime: datetime.datetime = kwargs.get("trade_datetime")
            trade_price = datetime.datetime = kwargs.get("trade_price")
            executor: str = kwargs.get("executor")
            parent_trade: Trade = kwargs.get("parent_trade")
            trade_type: str = "close"
            broker: str = "FakeBroker"

            data: dict = {
                "position_size": position_size,
                "position_stop_loss": position_stop_loss,
                "position_limit": position_limit,
                "symbol": symbol,
                "position_type": position_type,
                "trade_datetime": trade_datetime,
                "trade_price": trade_price,
                "trade_type": trade_type,
                "position_id": transaction_id,
                "broker": broker,
                "executor": executor,
                "parent_trade": parent_trade
            }
            trade: Trade = Trade.objects.create(**data)
            return trade.pk
        except Exception as e:
            return str(e)

    def get_data(self, *args, **kwargs):
        pass

    def create_order(self, *args, **kwargs):
        pass

    def cancel_order(self, *args, **kwargs):
        pass

