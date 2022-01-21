import yfinance as yf
import pandas as pd
from data.models import Data, Symbol, Timeframe
import pytz
from django.utils import timezone

class Provider:
    def __init__(self, symbol: Symbol, timeframe: Timeframe, period: str = None):
        self.symbol: Symbol = Symbol.objects.get(name = symbol)
        self.timeframe: Timeframe = Timeframe.objects.get(name = timeframe)
        self.period: str = period

    def get_data(self):
        return None

    def save_data(self, data):
        pass

    def run(self):
        data = self.get_data()
        self.save_data(data)



class YahooFinance(Provider):
    def get_data(self) -> pd.DataFrame:
        return yf.Ticker(self.symbol.name).history(interval=self.timeframe.name, period = self.period if self.period else "1y")

    def save_data(self, data: pd.DataFrame):
        if data.empty:
            raise Exception("No data was retreived")
        for counter, ind in enumerate(data.index):
            price_datetime = data.index[counter].astimezone(pytz.utc) if timezone.is_aware(data.index[counter]) else pytz.utc.localize(data.index[counter])
            data_obj = Data.objects.get_or_create(
                datetime = price_datetime,
                timeframe = self.timeframe,
                symbol = self.symbol,
                open_bid = data.Open.iloc[counter], 
                close_bid = data.Close.iloc[counter], 
                high_bid = data.High.iloc[counter], 
                low_bid = data.Low.iloc[counter], 
                volume = data.Volume.iloc[counter], 
            )
