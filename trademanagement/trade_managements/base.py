from django.db import transaction


class TradeManagementBase:
    def __init__(self, *args, **kwargs):
        self.Trade_management = kwargs["Trade_management"]
        self.indicators_parameter_dict = {}
        for parameter in self.Trade_management.indicators_configuration:
            self.indicators_parameter_dict[parameter["class"]
                                           ] = parameter["args"]

    def setup(self):
        if not self.Trade_management.storage:
            self.Trade_management.storage = {}
            self.Trade_management.save()

    def run(self, entry_price: float, *args, **kwargs):
        pass


class SampleTradeManagement(TradeManagementBase):
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
            print("SampleTradeManagement", e)
