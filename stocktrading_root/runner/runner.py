from strategy.models import Strategy
from typing import Union, List
import time
from django.core.management import call_command

class Runner:
    WAIT_TIME: int = 3 #seconds

    def __init__(self, *args, **kwargs):
        self.strategies: List[Strategy] = list(Strategy.objects.filter(active = True))

    def run(self):
        while True:
            for strategy in self.strategies:
                try:
                    strategy.run()
                except Exception as e:
                    print(f"Runner error for strategy {strategy.pk}", e)

            time.sleep(self.WAIT_TIME)