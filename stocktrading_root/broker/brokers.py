import yfinance as yf
import pandas as pd
from data.models import Data, Symbol, Timeframe
import pytz
from .models import Trade, BrokerStorage
import importlib

class Broker:

    @staticmethod
    def setup(module: str, *args, **kwargs) -> "Broker":
        broker_main_module = importlib.import_module("broker.brokers")
        broker_class = getattr(broker_main_module, module)
        broker = broker_class(*args, **kwargs)
        return broker

    def __init__(self, *args, **kwargs):
        self.storage, is_created = BrokerStorage.objects.get_or_create(broker = self.__class__.__name__)

    def connect(self):
        pass

    def get_account_info(self):
        pass

    def get_balance(self):
        pass

    def get_equity(self):
        pass

    def get_used_margin(self):
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
    def get_account_info(self):
        pass

    def get_balance(self):
        pass

    def get_equity(self):
        pass

    def get_used_margin(self):
        pass
    
    def open_position(self, *args, **kwargs):
        pass

    def close_position(self, *args, **kwargs):
        pass

    def get_data(self, *args, **kwargs):
        pass
