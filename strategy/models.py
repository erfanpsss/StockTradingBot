import importlib
import math
from operator import mod
import pickle
from django.core.management import call_command
import numpy as np
import pandas as pd
import tensorflow as tf
from account.models import Account
from data.models import Data
from django.conf import settings
from django.db import models
from django.db.models import (
    Avg,
    BooleanField,
    Case,
    Count,
    Exists,
    F,
    IntegerField,
    Max,
    Min,
    OuterRef,
    Q,
    Subquery,
    Sum,
    When,
)
from indicator.models import *
from keras.layers import LSTM, Dense
from keras.models import Sequential
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPClassifier, MLPRegressor
from broker.models import Broker

# from sklearn.svm import SVC
# from tensorflow import keras


def default_indicators_configuration():
    return [
        {"class": "MovingAverage", "args": {"period": 10}},
    ]


def default_symbol_timeframe_pair():
    return [
        {"AAPL": ["1h"]},
    ]


class Strategy(models.Model):
    strategy_choices = (("SampleStrategy", "SampleStrategy"),
                        ("Alpha", "Alpha"))
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=False)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="account_strategies")
    description = models.TextField(null=True, blank=True)
    indicators_configuration = models.JSONField(
        default=default_indicators_configuration
    )
    configurations = models.JSONField(
        null=True, blank=True, default=dict)
    strategy_class = models.CharField(max_length=200, choices=strategy_choices)
    storage = models.JSONField(null=True, blank=True, default=dict)
    strategy = None

    class Meta:
        verbose_name = "Strategy"
        verbose_name_plural = "Strategies"

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

    def init(self):
        module = importlib.import_module("strategy.strategies")
        strategy_class = getattr(module, self.strategy_class)
        conf = {"strategy": self}
        self.strategy: "Strategy" = strategy_class(**conf)

    def run(self):
        self.init()
        self.strategy.setup()
        return self.strategy.run()
