from django.db import transaction
from .base import RiskManagementBase
from trade.models import Trade
from typing import List, Tuple
from util.consts import OrderType, PositionType, TradeType
from indicator.models import Atr


class Alpha(RiskManagementBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buying_power = self.system.broker.buying_power
        self.allowed_trading_capital = self.risk_management.risk_management_configuration.get(
            "allowed_trading_capital")
        self.risk = self.risk_management.risk_management_configuration.get(
            "risk")
        self.max_percent_capital_allocation_per_trade = self.risk_management.risk_management_configuration.get(
            "max_percent_capital_allocation_per_trade")
        self.atr_multiply = self.risk_management.risk_management_configuration.get(
            "atr_multiply")

    def get_data(self, trade):
        entry_price = trade["trade_price"]
        symbol = trade["symbol_name"]
        timeframe = trade["timeframe"]
        current_atr = Atr.objects.filter(price_id__symbol__name=symbol, price_id__timeframe__name=timeframe).order_by(
            "price_id__datetime").last().value
        if not current_atr:
            raise Exception("No ATR")
        atr_product = current_atr * self.atr_multiply
        stoploss = entry_price - atr_product
        max_loss_per_share = entry_price - stoploss
        total_number_of_shares = self.risk / max_loss_per_share
        total_trade_size = total_number_of_shares * entry_price
        if total_trade_size > self.max_capital_allocation_per_trade:
            total_number_of_shares = self.max_capital_allocation_per_trade / max_loss_per_share
            total_trade_size = total_number_of_shares * entry_price
        return {
            "total_trade_size": total_trade_size,
            "total_number_of_shares": total_number_of_shares,
            "max_loss_per_share": max_loss_per_share,
            "stoploss": stoploss
        }

    @property
    def risk_amount(self):
        try:
            return self.risk * self.allowed_trading_capital
        except:
            return 0.0

    @property
    def max_capital_allocation_per_trade(self):
        try:
            return self.max_percent_capital_allocation_per_trade * self.allowed_trading_capital
        except:
            return 0.0

    def setup(self):
        super().setup()

    def run(self, trade, *args, **kwargs):
        super().run(trade, *args, **kwargs)
        prepared_trade = trade
        try:
            data = self.get_data(trade)
            prepared_trade["trade_size"] = data["total_trade_size"]
            prepared_trade["trade_stop_loss"] = data["stoploss"]
            prepared_trade["quantity"] = data["total_number_of_shares"]

        except Exception as e:
            print("Alpha", e)

        return prepared_trade
