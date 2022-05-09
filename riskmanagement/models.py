from django.db import models
import importlib

from account.models import Account


def default_indicators_configuration():
    return [
        {"class": "MovingAverage", "args": {"period": 10}},
        {"class": "ExponentialMovingAverage", "args": {"period": 10}},
    ]


class RiskManagement(models.Model):
    risk_management_choices = (("SampleRiskManagement", "SampleRiskManagement"),
                               ("Alpha", "Alpha"))
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="account_riskmanagements")

    name = models.CharField(unique=True, max_length=200)
    is_active = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    indicators_configuration = models.JSONField(
        default=default_indicators_configuration
    )
    allowed_trading_capital = models.FloatField(default=0.0)
    risk = models.FloatField(default=0.0)
    max_capital_allocation_per_trade_percent = models.FloatField(default=0.0)
    configurations = models.JSONField(default=dict, null=True, blank=True,)
    storage = models.JSONField(default=dict, null=True, blank=True,)
    created_on = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    risk_management_configuration = models.JSONField(
        null=True, blank=True, default=dict)
    risk_management_class = models.CharField(
        max_length=200, choices=risk_management_choices)
    risk_management = None

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Risk Management"
        verbose_name_plural = "Risk Managements"

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

    def init(self, system):
        module = importlib.import_module("riskmanagement.risk_management")
        risk_management_class = getattr(module, self.risk_management_class)
        conf = {"risk_management": self, "system": system}
        self.risk_management: "RiskManagement" = risk_management_class(**conf)

    def run(self, trades: list, system, *args, **kwargs):
        self.init(system)
        self.risk_management.setup()
        prepared_trades = []
        for trade in trades:
            prepared_trade = self.risk_management.run(trade, *args, **kwargs)
            if not prepared_trade:
                continue
            prepared_trades.append(prepared_trade)
        return prepared_trades
