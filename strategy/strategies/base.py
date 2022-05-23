from django.db import transaction


class StrategyBase:
    def __init__(self, *args, **kwargs):
        self.strategy = kwargs["strategy"]
        self.indicators_parameter_dict = {}
        for parameter in self.strategy.indicators_configuration:
            self.indicators_parameter_dict[parameter["class"]
                                           ] = parameter["args"]

    def setup(self):
        if not self.strategy.storage:
            self.strategy.storage = {}
            self.strategy.save(update_fields=['storage'])

    def run(self):
        return []


class SampleStrategy(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()

    def run(self):
        super().run()
        try:
            return []
        except Exception as e:
            print("SampleStrategy", e)
            return []
