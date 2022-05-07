from django.db import transaction
from .base import TradeManagementBase
from trade.models import Trade
from typing import List, Tuple
from util.consts import OrderType, PositionType, TradeType
from indicator.models import Atr
from data.models import Symbol
from data.models import Data


class Alpha(TradeManagementBase):
    STORAGE_TRADE_KEY = "trades"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.complementary_trades = []
        self.number_of_entries_per_decision = self.trade_management.trade_management_configuration.get(
            "number_of_entries_per_decision", 1)

        self.entries_configuration = self.trade_management.trade_management_configuration.get(
            "entries_configuration", {"1": {"allocation": 0.50}, "2": {"allocation": 0.50}})

        self.exits_configuration = self.trade_management.trade_management_configuration.get(
            "exits_configuration", {"1": {"allocation": 0.50}, "2": {"allocation": 0.50}})

    def setup(self):
        super().setup()
        if not self.trade_management.storage.get(self.STORAGE_TRADE_KEY):
            self.trade_management.storage = {self.STORAGE_TRADE_KEY: {}}
            self.trade_management.save(update_fields=["storage"])

    def get_entry_configurations(self):
        return dict(sorted(self.entries_configuration.items(), key=lambda x: int(x[0])))

    def get_exit_configurations(self):
        return dict(sorted(self.exits_configuration.items(), key=lambda x: int(x[0])))

    def entry_condition_1(self, parent_trade_obj):
        return True

    def check_entry_condition(self, parent_trade_obj):
        condition_methods = [
            self.entry_condition_1,
        ]
        for condition_method in condition_methods:
            if not condition_method(parent_trade_obj):
                return False
        return True

    def recalibrate_trade(self, trade, number):
        current_price = self.get_current_price(trade.symbol)
        price_diff = current_price - trade.trade_price
        configured_allocation = self.get_entry_configurations().get(number).get("allocation")
        parent_allocation = self.get_entry_configurations().get("1").get("allocation")
        diff_ratio = configured_allocation / parent_allocation
        return {
            "symbol_name": trade.symbol.name,
            "trade_price": current_price,
            "trade_stop_loss": trade.trade_stop_loss + price_diff if trade.trade_stop_loss else None,
            "trade_limit": trade.trade_limit + price_diff if trade.trade_limit else None,
            "order_type": trade.order_type,
            "trade_size": trade.trade_size * diff_ratio,
            "quantity": trade.quantity * diff_ratio,
            "main_quantity": trade.quantity * diff_ratio,
            "parent_trade": trade,
            "timeframe": trade.timeframe,
            "position_type": trade.position_type,
        }

    def discover_complementary_trade(self):

        for key, value in self.trade_management.storage.get(self.STORAGE_TRADE_KEY).items():
            parent_trade_obj = Trade.objects.get(pk=key)
            if len(value) < len(self.entries_configuration) and self.check_entry_condition(parent_trade_obj):
                trade_data = self.recalibrate_trade(
                    parent_trade_obj, len(value))
                self.complementary_trades.append(trade_data)

    def extra_logic_handler(self):
        self.discover_complementary_trade()
        for complementary_trade in self.complementary_trades:
            trade_obj = self.create_trade_obj_handler(complementary_trade)
            self.post_execute_trade_handler(trade_obj)

    def pre_execute_trade_handler(self, trade):
        allocation = self.entries_configuration.get(
            "1", {}).get("allocation", 1.00)
        trade_size = trade.get("trade_size") * allocation
        quantity = trade.get("quantity") * allocation
        trade["trade_size"] = trade_size
        trade["quantity"] = quantity
        trade["main_quantity"] = trade.get("quantity")
        return trade

    def post_execute_trade_handler(self, trade):
        trade_obj = super().post_execute_trade_handler(trade)
        trade_data = []
        if trade.parent_trade:
            key = str(trade_obj.parent_trade.pk)
            trade_data = self.trade_management.storage.get(self.STORAGE_TRADE_KEY).get(
                str(trade_obj.parent_trade.pk))
            if trade_data:
                trade_data.append(str(trade_obj.pk))
                trade_obj.parent_trade.filled_quantity = trade_obj.parent_trade.filled_quantity + trade.quantity
                trade_obj.parent_trade.save(update_fields=["filled_quantity"])
        else:
            key = str(trade_obj.pk)
        trade_storage_info = {key: trade_data}
        self.trade_management.add_or_update_storage(
            key=self.STORAGE_TRADE_KEY, value=trade_storage_info)
        return trade_obj

    def exit_trade_check_condition_handler(self, trade):
        last_close_price = self.get_current_price(trade.symbol)
        if trade.position_type == PositionType.BUY.value:
            if last_close_price > (trade.trade_price + trade.trade_price * (20/100)):
                return True
        return False

    def prepare_exit_trade_handler(self, trade):
        last_close_price = self.get_current_price(trade.symbol)
        return {
            "trade_type": TradeType.CLOSE.value,
            "parent_trade": trade,
            "symbol_name": trade.symbol,
            "trade_price": last_close_price + trade.trade_price * (1/100),
            "trade_stop_loss": None,
            "trade_limit": None,
            "order_type": OrderType.MKT.value,
            "trade_size": trade.trade_size,
            "quantity": trade.quantity,
            "position_type": PositionType.BUY.value if trade.position_type == PositionType.SELL.value else PositionType.SELL.value,
        }
