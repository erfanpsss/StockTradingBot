from django.db import transaction
from .base import StrategyBase
from trade.models import Trade
from typing import List, Tuple
from util.consts import OrderType, PositionType, TradeType
from indicator.models import Atr

class TradingSystem(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.risk_percent = self.strategy.strategy_configuration.get("risk_percent")


    def setup(self):
        super().setup()    

    def calculate_position_size_stoploss_limit(self) -> Tuple[float, float, float]:
        

        return 0.0, 0.0, 0.0

    def handle_manual_trades(self):
        strategy_trades: List[Trade] = self.strategy.strategy_trades.filter(is_executed = False)
        for strategy_trade in strategy_trades:
            current_symbol_timeframe_pair = self.strategy.symbol_timeframe_pair
            current_symbol_timeframe_pair.append({strategy_trade.symbol.name: ["1d"]})
            self.strategy.symbol_timeframe_pair = current_symbol_timeframe_pair
            self.strategy.save(update_fields = "symbol_timeframe_pair")
            self.strategy.get_data()
            quantity, stoploss, limit = self.calculate_position_size_stoploss_limit()
            strategy_trade.quantity = quantity
            strategy_trade.save(updated_fields = ["quantity"])
            strategy_trade.open_position()

        if stoploss:
            data: dict = {
                "trade_size": strategy_trade.trade_size,
                "position_stop_loss": strategy_trade.trade_stop_loss,
                "trade_limit": strategy_trade.trade_limit,
                "quantity": strategy_trade.quantity * -1,
                "symbol": strategy_trade.symbol,
                "order_type": OrderType.LMT.value,
                "price": stoploss,
                "position_type": PositionType.BUY.value if strategy_trade.position_type == PositionType.SELL.value else PositionType.SELL.value,
                "trade_type": TradeType.CLOSE.value,
                "broker": strategy_trade.broker,
                "executor": strategy_trade.executor,
            }
            stoploss_trade: Trade = Trade.objects.create(**data)
            stoploss_trade.open_position()


    def run(self):
        super().run()
        try:
            with transaction.atomic(): pass
                
                





        except Exception as e:
            print("TradingSystem", e)
