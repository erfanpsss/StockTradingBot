from django.db import transaction


class RiskManagementBase:
    def __init__(self, *args, **kwargs):
        self.risk_management = kwargs["risk_management"]
        self.indicators_parameter_dict = {}
        for parameter in self.risk_management.indicators_configuration:
            self.indicators_parameter_dict[parameter["class"]
                                           ] = parameter["args"]

    def setup(self):
        if not self.risk_management.storage:
            self.risk_management.storage = {}
            self.risk_management.save()

    def run(self, entry_price: float, *args, **kwargs):
        pass


class SampleRiskManagement(RiskManagementBase):
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
            print("SampleRiskManagement", e)
