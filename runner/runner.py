from strategy.models import Strategy
from typing import Union, List
import time
from django.core.management import call_command
from data.models import FinvizDataFile

class Runner:
    WAIT_TIME: int = 60 #seconds

    def __init__(self, *args, **kwargs):
        self.strategies: List[Strategy] = list(Strategy.objects.filter(active = True))

    def get_stock_data(self):
        FinvizDataFile.create_finviz_data_automatically()

    def run(self):
        while True:
            self.get_stock_data()
            for strategy in self.strategies:
                try:
                    strategy.run()
                except Exception as e:
                    print(f"Runner error for strategy {strategy.pk}", e)

            time.sleep(self.WAIT_TIME)