from django.db import models
from account.models import Account
from data.models import Data, Symbol
from util.models_choices import *
from broker.models import Broker
import datetime
from util.consts import *
import pytz
from system.models import System
import time

MAX_RETRY = 3
RETRY_WAIT = 3


class Trade(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="account_trades")
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
        Broker, on_delete=models.CASCADE, related_name="broker_trades")
    symbol = models.ForeignKey(
        Symbol, on_delete=models.CASCADE, related_name="trades")
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
        "self", on_delete=models.CASCADE, related_name="sub_trades", blank=True, null=True)
    executor = models.ForeignKey(
        System, on_delete=models.DO_NOTHING, related_name="system_trades", null=True, blank=True)
    is_executed = models.BooleanField(default=False)
    closed_quantity = models.FloatField(blank=True, null=True, default=0.0)

    sent_arguments = models.JSONField(default=dict, blank=True, null=True)
    error = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Trade"
        verbose_name_plural = "Trades"

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        is_new = False if self.pk else True
        super().save(*args, **kwargs)
        if is_new and self.place_now and not self.executor:
            self.open_position()

    @property
    def parent_trade_position_id(self):
        return self.parent_trade.position_id if self.parent_trade else ""

    def open_position(self):
        data: dict = {
            "trade_size": self.trade_size,
            "position_stop_loss": self.trade_stop_loss,
            "trade_limit": self.trade_limit,
            "quantity": self.quantity,
            "symbol": self.symbol.name,
            "order_type": self.order_type,
            "price": self.trade_price,
            "position_type": self.position_type,
            "trade_datetime": self.trade_datetime,
            "trade_price": self.trade_price,
            "trade_type": self.trade_type,
            "broker": self.broker,
            "executor": self.executor,
            "cOID": str(self.pk),
            "parent_trade_position_id": self.parent_trade_position_id
        }
        print("Opening position with data", data)
        try:
            for counter in range(MAX_RETRY):
                try:
                    transaction_id, status = self.broker.broker.open_position(
                        **data)
                    if not transaction_id:
                        print(transaction_id, status)
                        raise Exception("No transaction id returned")
                    self.position_id = transaction_id
                    self.status = status
                    break
                except Exception as e:
                    print(f"Try ({counter + 1})", str(e))
                    if counter == MAX_RETRY + 2:
                        raise Exception(str(e))
                    time.sleep(RETRY_WAIT)
        except Exception as e:
            print("Trade failed: open_position", e)
            self.position_id = ""
            self.error = str(e)
            self.status = TradeStatusList.FAILED.value
        self.is_executed = True
        self.save()

    @classmethod
    def close_position(cls, position, total=True, quantity=0, executor=None):
        if position.trade_type == TradeType.CLOSE.value:
            return

        trade = cls.objects.create(
            status=TradeStatusList.PENDING_SUBMIT.value,
            trade_type=TradeType.CLOSE.value,
            trade_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
            broker=position.broker,
            symbol=position.symbol,
            position_type=PositionType.SELL.value if position.position_type == PositionType.BUY.value else PositionType.BUY.value,
            quantity=position.quantity if total else quantity,
            parent_trade=position,
            executor=executor or position.executor,
            place_now=False
        )

        data: dict = {
            "trade_size": trade.trade_size,
            "trade_stop_loss": trade.trade_stop_loss,
            "trade_limit": trade.trade_limit,
            "quantity": trade.quantity,
            "symbol": trade.symbol.name,
            "position_type": trade.position_type,
            "trade_datetime": trade.trade_datetime,
            "trade_price": trade.trade_price,
            "trade_type": trade.trade_type,
            "broker": trade.broker,
            "executor": trade.executor,
            "parent_id": None,
            "cOID": str(trade.pk),
            "order_id": position.position_id,
        }
        try:
            transaction_id, status = trade.broker.broker.close_position(**data)
            if not transaction_id:
                raise Exception("No transaction id returned")
            trade.position_id = transaction_id
            trade.status = status
        except Exception as e:
            print(e)
            trade.position_id = ""
            trade.error = str(e)
            trade.status = TradeStatusList.FAILED.value
        trade.is_executed = True
        trade.save()

    @classmethod
    def refresh_positions_status(cls):
        trades = cls.objects.exclude(status__in=UPDATE_EXCLUDED_TRADE_STATUS)
        for trade in trades:
            try:
                status = trade.broker.broker.order_status(
                    *[], **{"order_id": trade.position_id})
                if status:
                    trade.status = trade.broker.broker.order_status(
                        *[], **{"order_id": trade.position_id})
                    trade.save()
            except Exception as e:
                print("refresh_positions_status", e)
