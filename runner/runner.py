from strategy.models import Strategy
from typing import Union, List
import time
from django.core.management import call_command
from data.models import FinvizDataFile, FinvizSectorDataFile, FinvizInsiderDataFile
from runner.models import RunnerStatus
import datetime
import pytz
from broker.models import Broker
from trade.models import Trade


class Runner:
    def __init__(self, *args, **kwargs):
        self.strategies: List[Strategy] = list(Strategy.objects.filter(active = True))
        self.runner_status = None

    def refresh_trade_status(self):
        Trade.refresh_positions_status()

    def broker_scheduled_calls(self):
        if self.runner_status.enable_broker_scheduled_calls:
            brokers = Broker.objects.all()
            for broker in brokers:
                try:
                    broker.run_scheduled_calls()
                except Exception as e:
                    print(e)
            self.refresh_trade_status()

    def get_stock_data(self):
        if self.runner_status.enable_finviz:
            FinvizDataFile.create_finviz_data_automatically()
            FinvizSectorDataFile.create_finviz_data_automatically()
            FinvizInsiderDataFile.create_finviz_data_automatically()

    def run(self):
        while True:
            print("Runner is running...")
            self.runner_status = RunnerStatus.objects.first()
            RunnerStatus.objects.update(last_run_time = pytz.utc.localize(datetime.datetime.utcnow()))
            if not self.runner_status.enable:
                break
            self.broker_scheduled_calls()
            self.get_stock_data()
            if self.runner_status.enable_strategies:
                for strategy in self.strategies:
                    try:
                        strategy.run()
                    except Exception as e:
                        print(f"Runner error for strategy {strategy.pk}", e)

            time.sleep(self.runner_status.loop_wait)