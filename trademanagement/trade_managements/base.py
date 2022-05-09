from re import M
from django.db import transaction
from data.models import Symbol
from trade.models import Trade
from django.db.models import F
from util.consts import TradeStatusList, PositionType, OrderType, TradeType
from data.models import Data


class TradeManagementBase:
    def __init__(self, *args, **kwargs):
        self.system = kwargs["system"]
        self.trade_management = kwargs["trade_management"]
        self.indicators_parameter_dict = {}
        for parameter in self.trade_management.indicators_configuration:
            self.indicators_parameter_dict[parameter["class"]
                                           ] = parameter["args"]

        self.existing_trades = []
        self.closing_trades = []
        self.closed_trades = []
        self.manual_trade_symbols = []
        self.automatic_trade_symbols = []
        self.prepared_trades = []
        self.trade_objects = []
        self.executed_trades = []

    def setup(self):
        if not self.trade_management.storage:
            self.trade_management.storage = {}
            self.trade_management.save()

    def get_current_price(self, symbol):
        return Data.last_close_price(symbol, self.system.base_timeframe)

    def get_existing_trades(self):
        self.existing_trades = list[self.system.broker.portfolio_open_trades_queryset.filter(
            executor=self.system)]

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

    def exit_trade_finder(self):
        for trade in self.existing_trades:
            if self.exit_trade_check_condition_handler(trade):
                prepared_trade = self.prepare_exit_trade_handler(trade)
                if prepared_trade:
                    self.closing_trades.append(prepared_trade)

    def exit_trade_handler(self):
        """To be overriden"""
        for closing_trade in self.closing_trades:
            trade_obj = self.create_trade_obj_handler(closing_trade)
            trade_obj = self.execute_trade_handler(trade_obj)
            trade_obj.parent_trade.closed_quantity = trade_obj.parent_trade.closed_quantity + \
                trade_obj.quantity
            trade_obj.parent_trade.save(update_fields=["closed_quantity"])
            self.closed_trades.append(trade_obj)

    def discover_exit_trade(self):
        self.get_existing_trades()
        self.exit_trade_finder()

    def execute_exit_trade(self):
        self.exit_trade_handler()

    def manual_trades(self):
        self.manual_trade_symbols = list(Trade.objects.filter(
            executor=self.system, is_executed=False).annotate(
                symbol_name=F("symbol__name")
        ).values(
                "pk",
                "symbol_name",
                "trade_price",
                "trade_stop_loss",
                "trade_limit",
                "order_type",
                "trade_size",
                "quantity",
                "position_type"
        )
        )

    def automatic_trades(self):
        self.automatic_trade_symbols = self.automatic_trade_handler()

    def dicover_trade(self):
        if self.system.is_active_manual_trade_handling:
            self.manual_trades()
        if self.system.is_active_automatic_trade_handling:
            self.automatic_trades()

    def subscribe_symbol_timeframe(self):
        if self.system.is_active_manual_trade_handling:
            for manual_trade in self.manual_trade_symbols:
                self.system.add_symbol_timeframe_pair(
                    self, manual_trade["sumbol_name"], self.system.base_timeframe.name)
                manual_trade["timeframe"] = self.system.base_timeframe.name
        if self.system.is_active_automatic_trade_handling:
            for automatic_trade in self.automatic_trade_symbols:
                self.system.add_symbol_timeframe_pair(
                    self, automatic_trade["sumbol_name"], automatic_trade["timeframe"])

    def prepare_trade(self):
        if self.system.is_active_manual_trade_handling:
            self.prepared_trades = self.system.risk_management.run(
                self.manual_trades, self.system)
        if self.system.is_active_automatic_trade_handling:
            self.prepared_trades += self.system.risk_management.run(
                self.automatic_trades, self.system)

    def create_trade_obj_handler(self, trade):
        if trade.get("pk"):
            trade_obj = Trade.objects.get(pk=trade.get("pk"))
            trade_obj.price = Data.last_close_price(
                symbol, self.system.timeframe)
            trade_obj.trade_stop_loss = trade.get("trade_stop_loss"),
            trade_obj.trade_limit = trade.get("trade_limit"),
            trade_obj.trade_size = trade.get("trade_size"),
            trade_obj.quantity = trade.get("quantity"),
            trade_obj.parent_trade = trade.get("parent"),
            trade_obj.position_type = trade.get("position_type "),
            trade_obj.main_quantity = trade.get(
                "main_quantity", trade.get("quantity")),
            trade_obj.filled_quantity = trade.get(
                "filled_quantity", trade.get("quantity")),
            trade_obj.save(
                update_fields=["trade_stop_loss", "trade_limit", "trade_size", "quantity"])
        else:
            symbol = Symbol.objects.get(name=trade.get("symbol_name"))
            trade_obj = Trade.objects.create(
                order_type=trade.get("order_type"),
                account=self.system.account,
                price=Data.last_close_price(symbol, self.system.timeframe),
                symbol=symbol,
                trade_price=trade.get("trade_price"),
                trade_stop_loss=trade.get("trade_stop_loss"),
                trade_limit=trade.get("trade_limit"),
                trade_size=trade.get("trade_size"),
                position_type=trade.get("position_type "),
                quantity=trade.get("quantity"),
                parent_trade=trade.get("parent"),
                main_quantity=trade.get(
                    "main_quantity", trade.get("quantity")),
                executor=self.system
            )

        return trade_obj

    def pre_execute_trade_handler(self, trade):
        return trade

    def execute_trade_handler(self, trade_obj):
        trade_obj.open_position()
        trade_obj.refresh_from_db()

        return trade_obj

    def post_execute_trade_handler(self, trade):
        trade.filled_quantity = trade.quantity
        trade.save(update_fields=["filled_quantity"])
        trade.refresh_from_db()
        return trade

    def execute_trade(self):
        for trade in self.prepared_trades:
            prepared_trade = self.pre_execute_trade_handler(trade)
            trade_obj = self.create_trade_obj_handler(prepared_trade)
            trade_obj = self.post_execute_trade_handler(trade_obj)
            self.trade_objects.append(trade_obj)
            self.executed_trades.append(self.execute_trade_handler(trade_obj))

    def automatic_trade_handler(self):
        trades = [{
            "pk": "",
            "symbol_name": "",
            "trade_price": "",
            "trade_stop_loss": "",
            "trade_limit": "",
            "order_type": "",
            "trade_size": "",
            "quantity": "",
            "position_type ": "",
            "parent_trade": "",
            "main_quantity": "",
            "timeframe": self.system.base_timeframe.name
        }]
        try:
            trades: list = self.system.strategy.run()
        except Exception as e:
            print("TradeManagementBase", e)

        return trades

    def extra_logic_handler(self):
        pass

    def run(self):
        self.discover_exit_trade()
        self.execute_exit_trade()
        self.dicover_trade()
        self.subscribe_symbol_timeframe()
        self.prepare_trade()
        self.execute_trade()
        self.extra_logic_handler()


class SampleTradeManagement(TradeManagementBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()
