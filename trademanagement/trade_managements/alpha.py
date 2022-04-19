from django.db import transaction
from .base import TradeManagementBase
from trade.models import Trade
from typing import List, Tuple
from util.consts import OrderType, PositionType, TradeType
from indicator.models import Atr


class Alpha(TradeManagementBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()

    def run(self, entry_price: float, *args, **kwargs):
        super().run(entry_price, *args, **kwargs)
        try:
            with transaction.atomic():
                pass

        except Exception as e:
            print("Alpha", e)
