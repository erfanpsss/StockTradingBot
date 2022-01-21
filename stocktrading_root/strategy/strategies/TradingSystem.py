from django.db import transaction
from .base import StrategyBase

class TradingSystem(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()

    def run(self):
        super().run()
        try:
            with transaction.atomic(): pass
                
                





        except Exception as e:
            print("SampleStrategy", e)
