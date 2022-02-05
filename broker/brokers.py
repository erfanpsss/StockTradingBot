import yfinance as yf
import pandas as pd
from data.models import Data, Symbol, Timeframe
import pytz
from .models import Trade, BrokerStorage
import importlib
import datetime
import uuid

class Broker:

    def __init__(self, is_sandbox, public_key, secret_key):
        self.is_sandbox = is_sandbox
        self.public_key = public_key
        self.secret_key = secret_key

    def connect(self):
        pass

    @property
    def account_info(self):
        pass

    @property
    def balance(self):
        pass

    @property
    def equity(self):
        pass

    @property
    def used_margin(self):
        pass

    def open_position(self, *args, **kwargs):
        pass

    def close_position(self, *args, **kwargs):
        pass

    def get_data(self, *args, **kwargs):
        pass

    def create_order(self, *args, **kwargs):
        pass

    def cancel_order(self, *args, **kwargs):
        pass





class InteractiveBrokers:

    def connect(self):
        pass

    @property
    def account_info(self):
        pass

    @property
    def balance(self):
        pass

    @property
    def equity(self):
        pass

    @property
    def used_margin(self):
        pass

    def open_position(self, *args, **kwargs):
        pass

    def close_position(self, *args, **kwargs):
        pass

    def get_data(self, *args, **kwargs):
        pass

    def create_order(self, *args, **kwargs):
        pass

    def cancel_order(self, *args, **kwargs):
        pass









class FakeBroker(Broker):
    ACCOUNT_INFO_FILE_NAME: str = "fake_broke_account_info.csv"
    INITIAL_BALANCE: float = 1000.0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.intial_balance = kwargs.get("balance") or self.INITIAL_BALANCE
        self.setup_account()

    def setup_account(self):
        if not self.storage.storage.get("account_info"):
            self.storage.storage = {
                "account_info": {
                    "balance": self.intial_balance,
                    "equity": self.intial_balance,
                    "used_margin": 0.0
                }
            }
            self.storage.save()

    @property
    def account_info(self) -> dict:
        return self.storage.storage.get("account_info")

    @property
    def balance(self) -> float:
        return self.account_info.get("balance")

    @property
    def equity(self) -> float:
        return self.account_info.get("equity")

    @property
    def used_margin(self) -> float:
        return self.account_info.get("used_margin")
    
    def open_position(self, *args, **kwargs):
        position_size: float = kwargs.get("position_size")
        position_stop_loss: float = kwargs.get("stop_loss")
        position_limit: float = kwargs.get("limit")
        symbol: Symbol = kwargs.get("symbol")
        position_type: str = kwargs.get("position_type")
        trade_datetime: datetime.datetime = kwargs.get("trade_datetime")
        trade_price = datetime.datetime = kwargs.get("trade_price")
        executor: str = kwargs.get("executor")
        trade_type: str = "open"
        position_id: str = (uuid.uuid4())
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
            "position_id": position_id,
            "broker": broker,
            "executor": executor
        }

        return position_id

    def close_position(self, *args, **kwargs):
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
        position_id: str = (uuid.uuid4())
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
            "position_id": position_id,
            "broker": broker,
            "executor": executor,
            "parent_trade": parent_trade
        }

        return position_id

    def get_data(self, *args, **kwargs):
        pass
