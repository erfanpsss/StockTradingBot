from django.db import models
import importlib

from account.models import Account


def default_indicators_configuration():
    return [
        {"class": "MovingAverage", "args": {"period": 10}},
        {"class": "ExponentialMovingAverage", "args": {"period": 10}},
    ]


class TradeManagement(models.Model):
    trade_management_choices = (("SampleTradeManagement", "SampleTradeManagement"),
                                ("Alpha", "Alpha"))
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="account_trademanagements")

    name = models.CharField(unique=True, max_length=200)
    is_active = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    indicators_configuration = models.JSONField(
        default=default_indicators_configuration
    )
    configurations = models.JSONField(default=dict, null=True, blank=True, )
    storage = models.JSONField(default=dict, null=True, blank=True,)
    created_on = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    trade_management_configuration = models.JSONField(
        null=True, blank=True, default=dict)
    trade_management_class = models.CharField(
        max_length=200, choices=trade_management_choices)
    trade_management = None

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Trade Management"
        verbose_name_plural = "Trade Managements"

    @classmethod
    def get_available_indicator_configuration(cls):
        # Available indicators and configuration format
        # AVAILABLE_INDICATORS = [
        #    {"class": "MOVING_AVERAGE", "args": {"period": 10}},
        #    {"class": "EXPONENTIAL_MOVING_AVERAGE", "args": {"period": 10}},
        # ]

        indicators_configurations_all = list(
            cls.objects.filter(active=True).values_list(
                "indicators_configuration", flat=True
            )
        )
        indicators_configurations = []
        for indicator_configuration in indicators_configurations_all:
            for conf in indicator_configuration:
                if conf not in indicators_configurations:
                    indicators_configurations.append(conf)
        return indicators_configurations

    def add_or_update_storage(self, key, value):
        current_storage = self.storage
        current_storage.update({key: value})
        self.storage = current_storage
        self.save(update_fields=["storage"])

    def remove_storage(self, key):
        try:
            current_storage = self.storage
            current_storage.pop(key)
            self.storage = current_storage
            self.save(update_fields=["storage"])
        except KeyError:
            pass

    def init(self, system):
        module = importlib.import_module("trademanagement.trade_management")
        trade_management_class = getattr(module, self.trade_management_class)
        conf = {"trade_management": self, "system": system}
        self.trade_management: "TradeManagement" = trade_management_class(
            **conf)

    def run(self, system):
        self.init(system)
        self.trade_management.setup()
        return self.trade_management.run()
