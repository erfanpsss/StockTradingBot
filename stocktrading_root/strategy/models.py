import importlib
import math
import pickle

import numpy as np
import pandas as pd
import tensorflow as tf
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


# from sklearn.svm import SVC
# from tensorflow import keras


def default_indicators_configuration():
    return [
        {"class": "MovingAverage", "args": {"period": 10}},
        {"class": "ExponentialMovingAverage", "args": {"period": 10}},
    ]


class Strategy(models.Model):
    strategy_choices = (("SampleStrategy", "SampleStrategy"),)

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    indicators_configuration = models.JSONField(
        default=default_indicators_configuration
    )
    strategy_configuration = models.JSONField(null=True, blank=True, default=dict)
    strategy_class = models.CharField(max_length=200, choices=strategy_choices)

    strategy_storage = models.JSONField(null=True, blank=True, default=dict)

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
        module = importlib.import_module("strategy.models")
        strategy_class = getattr(module, self.strategy_class)
        conf = {"strategy": self}
        self.strategy = strategy_class(**conf)

    def run(self):
        self.init()
        self.strategy.setup()
        return self.strategy.run()


class StrategyBase:
    B = 1  # Buy
    S = -1  # Sell
    N = 0  # Neutral
    EB = 2  # Exit Buy
    ES = -2  # Exit Sell

    def __init__(self, *args, **kwargs):
        self.strategy = kwargs["strategy"]
        self.indicators_parameter_dict = {}
        for parameter in self.strategy.indicators_configuration:
            self.indicators_parameter_dict[parameter["class"]] = parameter["args"]

    def setup(self):
        if not self.strategy.strategy_storage:
            self.strategy.strategy_storage = {}
            self.strategy.save()


    def run(self):
        pass


class SampleStrategy(StrategyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()

    def run(self):
        super().run()
        try:
            decision = self.N
            with transaction.atomic():
                pass
        except Exception as e:
            print("SampleStrategy", e)
            return decision


