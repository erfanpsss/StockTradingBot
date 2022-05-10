from system.models import System
from typing import Union, List
import time
from django.core.management import call_command
from data.models import FinvizDataFile, FinvizSectorDataFile, FinvizInsiderDataFile
from runner.models import RunnerStatus
import datetime
import pytz
from broker.models import Broker
from trade.models import Trade
import threading


class Runner:
    def __init__(self, *args, **kwargs):
        self.systems: List[System] = list(
            System.objects.filter(is_active=True))
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

    def keep_broker_session_alive_thread(self):
        brokers = Broker.objects.all()
        while True:
            print("Runner is pinging broker servers...")
            self.runner_status = RunnerStatus.objects.first()
            RunnerStatus.objects.update(
                last_run_time=pytz.utc.localize(datetime.datetime.utcnow()))
            if not self.runner_status.enable:
                break
            if self.runner_status.enable_broker_scheduled_calls:
                for broker in brokers:
                    try:
                        broker.broker.keep_auth_alive()
                    except Exception as e:
                        print(e)

            time.sleep(self.runner_status.loop_wait)

    def update_broker_account_trade_thread(self):
        while True:
            print("Runner is updating brokers' account and trades...")
            self.runner_status = RunnerStatus.objects.first()
            RunnerStatus.objects.update(
                last_run_time=pytz.utc.localize(datetime.datetime.utcnow()))
            if not self.runner_status.enable:
                break
            self.broker_scheduled_calls()
            time.sleep(self.runner_status.loop_wait)

    def run(self):
        thread_keep_broker_session_alive = threading.Thread(
            group=None, target=self.keep_broker_session_alive_thread, args=())
        thread_update_broker_account_trade = threading.Thread(
            group=None, target=self.update_broker_account_trade_thread, args=())
        thread_keep_broker_session_alive.start()
        thread_update_broker_account_trade.start()

        while True:
            print("Runner is running...")
            self.runner_status = RunnerStatus.objects.first()
            RunnerStatus.objects.update(
                last_run_time=pytz.utc.localize(datetime.datetime.utcnow()))
            if not self.runner_status.enable:
                break
            self.get_stock_data()
            if self.runner_status.enable_systems:
                for system in self.systems:
                    try:
                        system.run()
                    except Exception as e:
                        print(f"Runner error for system {system.pk}", e)

            time.sleep(self.runner_status.loop_wait)
