from django.db import transaction


class RiskManagementBase:
    def __init__(self, *args, **kwargs):
        self.system = kwargs["system"]
        self.risk_management = kwargs["risk_management"]
        self.indicators_parameter_dict = {}
        for parameter in self.risk_management.indicators_configuration:
            self.indicators_parameter_dict[parameter["class"]
                                           ] = parameter["args"]

    def setup(self):
        if not self.risk_management.storage:
            self.risk_management.storage = {}
            self.risk_management.save()

    def get_data(self, trade):
        entry_price = trade["trade_price"]
        symbol = trade["symbol_name"]
        timeframe = trade["timeframe"]
        return {
            "total_trade_size": 0,
            "total_number_of_shares": 0,
            "max_loss_per_share": 0,
            "stoploss": 0
        }

    def run(self, trade, *args, **kwargs):
        return {
            "pk": "",
            "symbol_name": "",
            "trade_price": "",
            "trade_stop_loss": "",
            "trade_limit": "",
            "order_type": "",
            "trade_size": "",
            "quantity": "",
            "timeframe": ""
        }


class SampleRiskManagement(RiskManagementBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()

    def run(self, trade, *args, **kwargs):
        super().run(trade, *args, **kwargs)
        try:
            with transaction.atomic():
                pass

        except Exception as e:
            print("SampleRiskManagement", e)
