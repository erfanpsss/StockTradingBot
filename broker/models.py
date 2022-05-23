from django.db.models import Sum, F
from account.models import Account
from util.consts import TradeStatusList, TradeType
from util.models_choices import *
from email.policy import default
from django.db import models
from data.models import Symbol
import importlib
import datetime
import uuid
from.brokers import BrokerEngine


class Broker(models.Model):
    id = models.AutoField(primary_key=True)
    user_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="account_broker")
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=50)
    account_id = models.CharField(max_length=255, blank=True, null=True)
    is_sandbox = models.BooleanField(default=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    public_key = models.CharField(max_length=255, blank=True, null=True)
    secret_key = models.CharField(max_length=255, blank=True, null=True)
    broker_class = models.CharField(
        max_length=50, choices=BROKERS_LIST_CHOICES)
    currency = models.CharField(
        max_length=50, choices=CURRENCY_LIST_CHOICES)
    storage = models.JSONField(default=dict, blank=True, null=True)
    balance = models.FloatField(default=0.0)
    equity = models.FloatField(default=0.0)
    buying_power = models.FloatField(default=0.0)
    used_margin = models.FloatField(default=0.0)
    connected = models.BooleanField(default=False)
    error = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Broker"
        verbose_name_plural = "Brokers"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.setup()

    def setup(self):
        pass

    def run_scheduled_calls(self):
        print("Updating connection")
        self.connection_update()
        print("Updating account info")
        self.refresh_account_info()

    @property
    def broker(self):
        return BrokerEngine(self.is_sandbox, self.public_key, self.secret_key, self.broker_class, self.account_id, self).broker_processor

    def connection_update(self):
        try:
            self.connected = self.broker.is_authenticated
            self.save()
            connection = self.broker.connect()
            self.connected = connection
            self.error = ""
            self.save()
            return connection
        except Exception as e:
            print("connection_update", e)
            self.connected = False
            self.error = str(e)
            self.save()
            return False

    def refresh_account_info(self):
        try:
            account_info = self.broker.account_info
            if account_info.get("balance") and account_info.get("equity") and account_info.get("buying_power"):
                self.balance = account_info.get("balance")
                self.equity = account_info.get("equity")
                self.buying_power = account_info.get("buying_power")
            current_storage = self.storage
            current_storage["account_balance_info"] = account_info
            self.storage = current_storage
            self.save()
        except Exception as e:
            print("refresh_account_info", e)

    @property
    def account_info(self):
        return f"Balance: {self.balance}, equity: {self.equity}"

    @property
    def _portfolio_queryset(self):
        return self.broker_trades.values("symbol").filter(
            status__in=[TradeStatusList.FILLED.value]).annotate(total=Sum("quantity"), symbol_name=F("symbol__name")).filter(total__gt=0)

    @property
    def portfolio(self):
        return list(self._portfolio_queryset)

    @property
    def portfolio_symbols(self):

        return list(self._portfolio_queryset.values_list("symbol_name", flat=True))

    @property
    def portfolio_open_trades_queryset(self):
        return self.broker_trades.filter(
            trade_type=TradeType.OPEN.value,
            symbol__name__in=self.portfolio_symbols,
            status__in=[TradeStatusList.FILLED.value]).exclude(closed_quantity=F("main_quantity")).exclude(parent_trade__closed_quantity=F("parent_trade__main_quantity"))

    @property
    def symbol_holdings(self, symbol):
        holdings = self._portfolio_queryset().filter(symbol=symbol).first()
        if holdings:
            return holdings.total
        return 0

    def add_or_update_storage(self, key, value):
        current_storage = self.storage
        current_storage.update({key: value})
        self.storage = current_storage
        self.save(update_fields=["storage"])

    def remove_storage(self, key):
        try:
            current_storage = self.storage
            current_storage.pop(key)
            self.storage = current_storage
            self.save(update_fields=["storage"])
        except KeyError:
            pass
