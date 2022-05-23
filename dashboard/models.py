from django.db import models
from system.models import System
from django.db.models import Sum
from trade.models import Trade
from account.models import Account
from data.models import Data, Symbol
from util.models_choices import *
from broker.models import Broker
from util.consts import *


class ViewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(status__in=[TradeStatusList.CANCELLED.value, TradeStatusList.FAILED.value])


class Position(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="view_account_trades")
    price_data = models.ForeignKey(
        Data, on_delete=models.SET_NULL, null=True, blank=True)
    place_now = models.BooleanField(default=True)
    status = models.CharField(max_length=50, choices=TRADE_STATUS_CHOICES,
                              default=TradeStatusList.PENDING_SUBMIT.value)
    trade_type = models.CharField(
        max_length=10, choices=TRADE_TYPES_CHOICES, default=TradeType.OPEN.value)
    order_type = models.CharField(
        max_length=10, choices=ORDER_TYPE_CHOICES, default=OrderType.MKT.value)
    created_at = models.DateTimeField(auto_now_add=True)
    trade_datetime = models.DateTimeField(blank=True, null=True)
    broker = models.ForeignKey(
        Broker, on_delete=models.CASCADE, related_name="view_broker_trades")
    symbol = models.ForeignKey(
        Symbol, on_delete=models.CASCADE, related_name="view_trades")
    position_id = models.CharField(max_length=200, blank=True, null=True)
    position_type = models.CharField(max_length=10, choices=POSITION_TYPES)
    trade_price = models.FloatField(blank=True, null=True)
    trade_size = models.FloatField(blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    main_quantity = models.FloatField(blank=True, null=True)
    filled_quantity = models.FloatField(blank=True, null=True)
    trade_stop_loss = models.FloatField(blank=True, null=True)
    trade_limit = models.FloatField(blank=True, null=True)
    parent_trade = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="view_sub_trades", blank=True, null=True)
    executor = models.ForeignKey(
        System, on_delete=models.DO_NOTHING, related_name="view_system_trades", null=True, blank=True)
    is_executed = models.BooleanField(default=False)
    closed_quantity = models.FloatField(blank=True, null=True, default=0.0)

    sent_arguments = models.JSONField(default=dict, blank=True, null=True)
    error = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = Trade._meta.db_table

    objects = ViewManager()

    def save(self, *args, **kwargs):
        pass
