from django.db import models
from data.models import Data
import decimal
import importlib
import json
import math
import threading

import numpy as np
import pandas as pd
from django.conf import settings
from django.core.files.base import ContentFile, File
from django.db import models, transaction
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
from keras.layers import LSTM, Dense
from keras.models import Sequential
from keras.utils.generic_utils import default
from numpy.lib.arraysetops import unique
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPClassifier, MLPRegressor

INDICATORS_LIST = (
    ("MovingAverage", "MovingAverage"),
    ("ExponentialMovingAverage", "ExponentialMovingAverage"),
    ("Atr", "Atr"),
    ("NormalizePrice", "NormalizePrice"),
    ("GrowthBasedPrice", "GrowthBasedPrice"),
    ("RelativeGrowthBasedPrice", "RelativeGrowthBasedPrice"),
    ("RelativeWickGrowthBasedPrice", "RelativeWickGrowthBasedPrice"),
    ("LstmSignalGenerator", "LstmSignalGenerator"),
)


class IndicatorStorage(models.Model):
    id = models.AutoField(primary_key=True)
    indicator = models.TextField(unique=True)
    storage = models.JSONField(null=True, blank=True, default=dict)
    class Meta:
        verbose_name = "Indicator storage"
        verbose_name_plural = "Indicator storages"


class IndicatorBase(models.Model):
    price_id = models.ForeignKey(
        Data, on_delete=models.CASCADE, related_name="base"
    )
    sub_indicator_configuration = models.JSONField(null=True, blank=True)
    parameters = []
    values_output = []

    def calculate(self):
        pass

    @property
    def storage_initial(self):
        return {}

    def setup_storage(self):
        if self.storage.storage == {}:
            pass

    def get_parameters_value(self):
        return {parameter: getattr(self, parameter) for parameter in self.parameters}

    def calculate_sub_indicators(self):
        if not self.sub_indicator_configuration:
            return
        for indicator in self.sub_indicator_configuration:
            try:
                with transaction.atomic():
                    module = importlib.import_module("indicator.models")
                    indicator_class = getattr(module, indicator["class"])
                    temp_obj = indicator_class(**indicator["args"])
                    temp_obj.price_id = self.price_id
                    temp_obj.pre_save()
                    temp_obj.save()

            except Exception as e:
                pass

    @property
    def sub_indicators_dict_queryset(self) -> dict:
        dict_queryset = {}
        if not self.sub_indicator_configuration:
            return dict_queryset
        for indicator in self.sub_indicator_configuration:
            try:
                module = importlib.import_module("indicator.models")
                indicator_class = getattr(module, indicator["class"])
                temp_queryset = (
                    indicator_class.objects.filter(**indicator["args"])
                    .filter(
                        price_id__symbol=self.price_id.symbol,
                        price_id__timeframe=self.price_id.timeframe,
                    )
                    .order_by("price_id__datetime")
                )
                dict_queryset[
                    temp_queryset.first().indicator_config_name
                ] = temp_queryset
            except Exception as e:
                print("sub_indicators_dict_queryset", e)
        return dict_queryset

    @property
    def sub_indicators_len(self) -> dict:
        dict_indicators = {}
        for indicator, value in self.sub_indicators_dict_queryset.items():
            try:
                temp_value = value
                for val in temp_value.first().values_output:
                    temp_value = temp_value.exclude(**{val: None}).exclude(
                        **{val: decimal.Decimal("NaN")}
                    )
                dict_indicators[indicator] = temp_value.count()
            except Exception as e:
                print("sub_indicators_len", e)
        return dict_indicators

    @property
    def sub_indicators_dict_sorted_queryset(self) -> dict:
        dict_queryset = {}
        for indicator, value in self.sub_indicators_dict_queryset.items():
            try:
                temp_value = value
                for val in temp_value.first().values_output:
                    temp_value = temp_value.exclude(**{val: None}).exclude(
                        **{val: decimal.Decimal("NaN")}
                    )
                dict_queryset[indicator] = temp_value.order_by("price_id__datetime")

            except Exception as e:
                print("sub_indicators_dict_sorted_queryset", e)
        return dict_queryset

    @property
    def previous_obj(self):

        value = (
            self.__class__.objects.filter(Q(**self.get_parameters_value()))
            .filter(price_id__datetime__lt=self.price_id.datetime)
            .order_by("price_id__datetime")
            .last()
        )
        return value


    @property
    def previous_value(self):
        return self.previous_obj.value if self.previous_obj.value else None

    @property
    def indicator_config_name(self):
        args_str = str(
            {str(key): str(value) for key, value in self.get_parameters_value().items()}
        )
        whole_name = f"{self.__class__.__name__}{args_str}"
        name = (
            whole_name.replace(" ", "_")
            .replace("{", "_")
            .replace("[", "_")
            .replace("]", "_")
            .replace("}", "_")
            .replace(":", "_")
            .replace("'", "_")
            .replace(",", "_")
            .replace(",", "_")
            .replace('"', "_")
        )

        return name

    def create_storage(self):
        storage = IndicatorStorage.objects.filter(
            indicator=self.indicator_config_name
        ).first()
        if storage:
            return storage
        return IndicatorStorage.objects.create(
            indicator=self.indicator_config_name, storage=self.storage_initial
        )

    def set_storage(self, field, value):
        s = IndicatorStorage.objects.get(indicator=self.indicator_config_name)
        s.storage[field] = value
        s.save(update_fields=["storage"])
        s.refresh_from_db()

    @property
    def storage(self):
        return IndicatorStorage.objects.get(indicator=self.indicator_config_name)

    def pre_save(self, *args, **kwargs):
        self.create_storage()
        self.calculate_sub_indicators()
        self.calculate()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class MovingAverage(IndicatorBase):
    id = models.BigAutoField(primary_key=True)
    price_id = models.ForeignKey(
        Data, on_delete=models.CASCADE, related_name="ma"
    )
    # parameters
    period = models.IntegerField()
    # values
    value = models.FloatField()

    parameters = [
        "period",
    ]
    values_output = [
        "value",
    ]

    class Meta:
        unique_together = ("period", "price_id")

    def calculate(self):
        """
        The moving average is calculated by adding a stock's prices over a certain period
        and dividing the sum by the total number of periods.
        """
        try:
            self.value = 0.0
            if not self.previous_obj:
                return

            data = MovingAverage.objects.filter(
                Q(price_id__symbol=self.price_id.symbol)
                & Q(price_id__timeframe=self.price_id.timeframe)
                & Q(period=self.period)
            ).order_by("-price_id__datetime")[: self.period]

            self.value = sum(
                data.values_list("price_id__close_bid", flat=True)
            ) / len(data)
        except Exception as e:
            print("MovingAverage", e)
            self.value = 0.0


class ExponentialMovingAverage(IndicatorBase):
    id = models.BigAutoField(primary_key=True)
    price_id = models.ForeignKey(
        Data, on_delete=models.CASCADE, related_name="ema"
    )
    # parameters
    period = models.IntegerField()
    # values
    value = models.FloatField()

    class Meta:
        unique_together = ("period", "price_id")

    def calculate(self):
        """
        multiplier = [2 ÷ (period + 1)]

        EMA = Closing price x multiplier + EMA (previous day) x (1-multiplier)
        """
        try:
            self.value = 0.0
            if not self.previous_obj:
                return

            multiplier = 2 / (self.period + 1)

            previous_value = self.previous_value
            if not previous_value:
                data = ExponentialMovingAverage.objects.filter(
                    Q(price_id__symbol=self.price_id.symbol)
                    & Q(price_id__timeframe=self.price_id.timeframe)
                    & Q(period=self.period)
                ).order_by("-price_id__datetime",)[: self.period]
                self.value = sum(
                    data.values_list("price_id__close_bid", flat=True)
                ) / len(data)

            self.value = self.price_id.price * multiplier + previous_value * (
                1 - multiplier
            )

        except Exception as e:
            print("ExponentialMovingAverage", e)
            self.value = 0.0


class Atr(IndicatorBase):
    id = models.BigAutoField(primary_key=True)
    price_id = models.ForeignKey(
        Data, on_delete=models.CASCADE, related_name="atr"
    )
    # parameters
    period = models.IntegerField()
    # values
    value = models.FloatField()

    parameters = [
        "period",
    ]
    values_output = [
        "value",
    ]

    class Meta:
        unique_together = ("period", "price_id")

    def calculate(self):
        """
        The average true range (Atr) is calculated as below:
        -Firstly, TR needs to be discovered.
            true range (TR) is the greatest of the following:
                -Current high minus the previous close
                -Current low minus the previous close
                -Current high minus the current low

            true range = max[(high - low), abs(high - previous close), abs (low - previous close)]

        -Secondly, calculate Atr.
            Current Atr = ((Prior Atr x 13) + Current TR) / 14
        """
        try:
            self.value = 0.0
            if not self.previous_obj:
                return
            tr = max(
                (self.price_id.high_bid - self.price_id.low_bid),
                (self.price_id.high_bid - self.price_id.previous_value),
                (self.price_id.low_bid - self.price_id.previous_value),
            )
            self.value = ((self.previous_value * (self.period - 1)) + tr) / self.period
        except Exception as e:
            print("Atr", e)
            self.value = 0.0


class Macd(IndicatorBase):
    id = models.BigAutoField(primary_key=True)
    price_id = models.ForeignKey(
        Data, on_delete=models.CASCADE, related_name="macd"
    )
    # parameters
    long_period = models.IntegerField()
    short_period = models.IntegerField()
    signal_period = models.IntegerField()
    # values
    value = models.FloatField()
    signal = models.FloatField()

    class Meta:
        unique_together = ("price_id", "long_period", "short_period", "signal_period")

    def calculate(self):
        """
        Macd.
        """
        try:
            self.value = 0.0
            if not self.previous_obj:
                return

            data = MovingAverage.objects.filter(
                Q(price_id__symbol=self.price_id.symbol) & Q(period=self.period)
            ).order_by("-price_id__datetime",)[: self.period]
            self.value = sum(data.values_list("price_id__price_bid", flat=True)) / len(
                data
            )
        except Exception as e:
            print("Macd", e)
            self.value = 0.0


class NormalizePrice(IndicatorBase):
    id = models.BigAutoField(primary_key=True)
    price_id = models.ForeignKey(
        Data, on_delete=models.CASCADE, related_name="normalize"
    )
    # parameters
    period = models.IntegerField()
    # values
    value = models.FloatField()

    parameters = [
        "period",
    ]
    values_output = [
        "value",
    ]

    class Meta:
        unique_together = ("period", "price_id")

    def calculate(self):
        """
        Normalization formula
        y = (x - min) / (max - min)
        """
        try:
            self.value = self.price_id.price
            if not self.previous_obj:
                return

            period_max, period_min = list(
                NormalizePrice.objects.filter(
                    Q(price_id__symbol=self.price_id.symbol)
                    & Q(price_id__timeframe=self.price_id.timeframe)
                    & Q(period=self.period)
                )
                .order_by(
                    "-price_id__datetime",
                )[: self.period]
                .aggregate(max=Max("value"), min=Min("value"))
                .values()
            )

            difference = period_max - period_min
            difference = difference if difference != 0.0 else self.price_id.price
            self.value = (self.price_id.price - period_min) / difference

        except Exception as e:
            print("NormalizePrice", e)
            self.value = self.price_id.price


class GrowthBasedPrice(IndicatorBase):
    id = models.BigAutoField(primary_key=True)
    price_id = models.ForeignKey(
        Data, on_delete=models.CASCADE, related_name="growth_based"
    )
    # parameters
    period = models.IntegerField()
    # values
    value = models.FloatField()

    parameters = [
        "period",
    ]
    values_output = [
        "value",
    ]

    class Meta:
        unique_together = ("period", "price_id")

    def calculate(self):
        """
        1 is green
        -1 is red
        0 is neutral

        """
        try:
            self.value = 0.0
            if not self.previous_obj:
                return
            if self.previous_obj.price_id.price < self.price_id.price:
                self.value = 1
            elif self.previous_obj.price_id.price > self.price_id.price:
                self.value = -1
            else:
                self.value = 0

        except Exception as e:
            print("GrowthBasedPrice", e)
            self.value = 0


class RelativeGrowthBasedPrice(IndicatorBase):
    id = models.BigAutoField(primary_key=True)
    price_id = models.ForeignKey(
        Data, on_delete=models.CASCADE, related_name="relative_growth_based"
    )
    # parameters
    period = models.IntegerField()
    # values
    value = models.FloatField()

    parameters = [
        "period",
    ]
    values_output = [
        "value",
    ]

    class Meta:
        unique_together = ("period", "price_id")

    def calculate(self):
        """
        4 over 4x previous candle green
        3 3x previous candle green
        2 2x previous candle green
        1 1x previous candle green
        0 neutral
        -1 1x previous candle red
        -2 2x previous candle red
        -3 3x previous candle red
        -4 over 4x previous candle red
        """
        try:
            self.value = 0.0
            if not self.previous_obj:
                return

            is_neutral = self.price_id.close_bid == self.price_id.open_bid
            is_green = self.price_id.close_bid > self.price_id.open_bid
            current_candle_body_size = abs(
                self.price_id.close_bid - self.price_id.open_bid
            )

            previous_candle_body_size = abs(
                self.previous_obj.price_id.close_bid
                - self.previous_obj.price_id.open_bid
            )
            if (
                current_candle_body_size > previous_candle_body_size
                and current_candle_body_size < previous_candle_body_size * 2
            ):
                self.value = 1
            elif (
                current_candle_body_size > previous_candle_body_size * 2
                and current_candle_body_size < previous_candle_body_size * 3
            ):
                self.value = 2
            elif (
                current_candle_body_size > previous_candle_body_size * 3
                and current_candle_body_size < previous_candle_body_size * 4
            ):
                self.value = 3
            elif current_candle_body_size > previous_candle_body_size * 4:
                self.value = 4
            if not is_green and not is_neutral:
                self.value *= -1

        except Exception as e:
            print("RelativeGrowthBasedPrice", e)
            self.value = 0


class RelativeWickGrowthBasedPrice(IndicatorBase):
    candle_type_choices = (
        ("HAMMER BEARISH", "HAMMER BEARISH"),
        ("HAMMER BULLISH", "HAMMER BULLISH"),
        ("UNKNOWN", "UNKNOWN"),
    )
    id = models.BigAutoField(primary_key=True)
    price_id = models.ForeignKey(
        Data, on_delete=models.CASCADE, related_name="relative_wick_growth_based"
    )

    # parameters
    period = models.IntegerField()
    # values
    value = models.FloatField()

    up_wick = models.FloatField()

    down_wick = models.FloatField()

    candle_type = models.CharField(
        max_length=200, choices=candle_type_choices, default="UNKNOWN"
    )

    parameters = [
        "period",
    ]
    values_output = [
        "value",
        "up_wick",
        "down_wick",
        # "candle_type",
    ]

    class Meta:
        unique_together = ("period", "price_id")

    @property
    def is_neutral(self):
        return self.price_id.close_bid == self.price_id.open_bid

    @property
    def is_green(self):
        return self.price_id.close_bid > self.price_id.open_bid

    def calculate(self):
        """
        4 over 4x previous candle green
        3 3x previous candle green
        2 2x previous candle green
        1 1x previous candle green
        0 neutral
        -1 1x previous candle red
        -2 2x previous candle red
        -3 3x previous candle red
        -4 over 4x previous candle red
        """
        try:
            self.value = 0.0
            self.up_wick = 0.0
            self.down_wick = 0.0
            if not self.previous_obj:
                return

            if self.is_green:
                current_up_wick_size = (
                    self.price_id.high_bid - self.price_id.close_bid
                )
                current_down_wick_size = (
                    self.price_id.open_bid - self.price_id.low_bid
                )
            else:
                current_up_wick_size = (
                    self.price_id.high_bid - self.price_id.open_bid
                )
                current_down_wick_size = (
                    self.price_id.close_bid - self.price_id.low_bid
                )

            if self.previous_obj.is_green:
                previous_up_wick_size = (
                    self.previous_obj.price_id.high_bid
                    - self.previous_obj.price_id.close_bid
                )
                previous_down_wick_size = (
                    self.previous_obj.price_id.open_bid
                    - self.previous_obj.price_id.low_bid
                )
            else:
                previous_up_wick_size = (
                    self.previous_obj.price_id.high_bid
                    - self.previous_obj.price_id.open_bid
                )
                previous_down_wick_size = (
                    self.previous_obj.price_id.close_bid
                    - self.previous_obj.price_id.low_bid
                )

            current_candle_body_size = abs(
                (self.price_id.high_bid - self.price_id.low_bid)
                - abs(self.price_id.close_bid - self.price_id.open_bid)
            )
            previous_candle_body_size = abs(
                (
                    self.previous_obj.price_id.high_bid
                    - self.previous_obj.price_id.low_bid
                )
                - abs(
                    self.previous_obj.price_id.close_bid
                    - self.previous_obj.price_id.open_bid
                )
            )
            if (
                current_up_wick_size > previous_up_wick_size
                and current_up_wick_size < previous_up_wick_size * 2
            ):
                self.up_wick = 1
            elif (
                current_up_wick_size > previous_up_wick_size * 2
                and current_up_wick_size < previous_up_wick_size * 3
            ):
                self.up_wick = 2
            elif (
                current_up_wick_size > previous_up_wick_size * 3
                and current_up_wick_size < previous_up_wick_size * 4
            ):
                self.up_wick = 3
            elif current_up_wick_size > previous_up_wick_size * 4:
                self.up_wick = 4

            if (
                current_down_wick_size > previous_down_wick_size
                and current_down_wick_size < previous_down_wick_size * 2
            ):
                self.down_wick = 1
            elif (
                current_down_wick_size > previous_down_wick_size * 2
                and current_down_wick_size < previous_down_wick_size * 3
            ):
                self.down_wick = 2
            elif (
                current_down_wick_size > previous_down_wick_size * 3
                and current_down_wick_size < previous_down_wick_size * 4
            ):
                self.down_wick = 3
            elif current_down_wick_size > previous_down_wick_size * 4:
                self.down_wick = 4

            if (
                current_candle_body_size > previous_candle_body_size
                and current_candle_body_size < previous_candle_body_size * 2
            ):
                self.value = 1
            elif (
                current_candle_body_size > previous_candle_body_size * 2
                and current_candle_body_size < previous_candle_body_size * 3
            ):
                self.value = 2
            elif (
                current_candle_body_size > previous_candle_body_size * 3
                and current_candle_body_size < previous_candle_body_size * 4
            ):
                self.value = 3
            elif current_candle_body_size > previous_candle_body_size * 4:
                self.value = 4

            if self.up_wick > self.down_wick:
                self.candle_type = "HAMMER BEARISH"
            elif self.up_wick < self.down_wick:
                self.candle_type = "HAMMER BULLISH"

            if not self.is_green and not self.is_neutral:
                self.value *= -1
                self.up_wick *= -1
                self.down_wick *= -1

        except Exception as e:
            print("RelativeWickGrowthBasedPrice", e)
            self.value = 0
            self.up_wick = 0
            self.down_wick = 0


class LstmSignalGenerator(IndicatorBase):
    id = models.BigAutoField(primary_key=True)
    price_id = models.ForeignKey(
        Data, on_delete=models.CASCADE, related_name="lstm_signal_generator"
    )
    # parameters
    name = models.CharField(max_length=50)
    min_data_length = models.IntegerField(default=500)
    max_data_length = models.IntegerField(blank=True, null=True)
    remodel = models.BooleanField(default=False)
    remodel_after = models.IntegerField(blank=True, null=True)
    lag = models.IntegerField(default=7)
    epoch = models.IntegerField(default=2000)
    dense = models.IntegerField(default=1)
    sub_indicator_configuration = models.JSONField()
    output_configuration = models.JSONField()
    output_value = models.TextField()
    # values
    value = models.FloatField()

    parameters = [
        "name",
        "min_data_length",
        "max_data_length",
        "remodel",
        "remodel_after",
        "lag",
        "epoch",
        "sub_indicator_configuration",
        "output_configuration",
        "output_value",
    ]
    values_output = [
        "value",
    ]

    class Meta:
        unique_together = ("name", "price_id")

    @property
    def output_column_name(self):
        output_configuration_str = str(
            {
                str(key): str(value)
                for key, value in self.output_configuration["args"].items()
            }
        )
        column_name_raw = f"{self.output_configuration['class']}{output_configuration_str}_{self.output_value}"
        column_name = (
            column_name_raw.replace(" ", "_")
            .replace("{", "_")
            .replace("[", "_")
            .replace("]", "_")
            .replace("}", "_")
            .replace(":", "_")
            .replace("'", "")
            .replace('"', "")
        )
        return column_name

    @property
    def inputs(self):
        dict_queryset = {}
        for indicator, value in self.sub_indicators_dict_sorted_queryset.items():
            try:
                if not int(self.max_data_length) or value.count() <= int(
                    self.max_data_length
                ):
                    temp_value = value[:]
                elif value.count() > int(self.max_data_length):
                    temp_value = value[: int(self.max_data_length)]
                else:
                    return {}
                for output in temp_value.first().values_output:
                    dict_queryset[f"{indicator}_{output}"] = list(
                        value.values_list(output, flat=True)
                    )

            except Exception as e:
                return {}
        return dict_queryset

    def prepare_data(self, input_data):
        default_columns = list(input_data.columns)
        x_columns = default_columns.copy()
        for lag in range(1, int(self.lag) + 1):
            if lag == 1:
                for col in default_columns:
                    input_data[f"{col}_{str(lag)}"] = input_data[col].shift(1)
                    x_columns.append(f"{col}_{str(lag)}")
                    if col == self.output_column_name:
                        input_data[col + "_next"] = input_data[col].shift(-1)
            else:
                for col in default_columns:
                    input_data[f"{col}_{str(lag)}"] = input_data[
                        f"{col}_{str(lag - 1)}"
                    ].shift(1)
                    x_columns.append(f"{col}_{str(lag)}")
                    if col == self.output_column_name:
                        input_data[col + "_next"] = input_data[col].shift(-1)

        return input_data[int(self.lag) + 1 :], x_columns

    @property
    def storage_initial(self):
        return {
            "is_training": False,
            "is_trained": False,
            "lstm_model": "",
        }

    def train_model(self):
        try:
            if any(
                count < int(self.min_data_length)
                for indicator, count in self.sub_indicators_len.items()
            ):
                return

            self.set_storage("is_training", True)
            input_data = pd.DataFrame(self.inputs)

            data, x_columns = self.prepare_data(input_data)
            x = data[:-1][x_columns]
            y = data[:-1][self.output_column_name + "_next"]
            with open("info.txt", "w") as f:
                f.write(f"1111\n{data}\n2222\n{y}\n3333\n{x}")
            x = np.array(x)
            x = x.reshape((x.shape[0], 1, x.shape[1]))
            y = np.array(y)
            model = Sequential()
            model.add(
                LSTM(
                    len(x_columns),
                    return_sequences=True,
                    input_shape=(x.shape[1], len(x_columns)),
                )
            )
            model.add(LSTM(len(x_columns), input_shape=(x.shape[1], len(x_columns))))
            model.add(Dense(int(self.dense)))
            model.compile(loss="mean_squared_error", optimizer="adam")
            model.fit(
                x,
                y,
                epochs=int(self.epoch),
                batch_size=int(self.lag),
                verbose=1,
                shuffle=False,
            )
            model.save_weights(
                f"{settings.BASE_DIR}/media/ml_models/lstm_model_{self.storage.pk}.h5",
            )
            self.set_storage(
                "lstm_model",
                f"{settings.BASE_DIR}/media/ml_models/lstm_model_{self.storage.pk}.h5",
            )
            self.set_storage("is_training", False)
            self.set_storage("is_trained", True)
        except Exception as e:
            print("train_model", e)
            self.set_storage("is_training", False)

    def calculate(self):
        """ """
        try:
            self.value = 0.0
            if self.storage.storage["is_training"]:
                return
            elif any(
                count < int(self.min_data_length)
                for indicator, count in self.sub_indicators_len.items()
            ):
                return
            elif not self.storage.storage["is_trained"]:
                thread = threading.Thread(target=self.train_model, args=())
                thread.start()
                return
            input_data = pd.DataFrame(self.inputs)
            data, x_columns = self.prepare_data(input_data)
            x = data[:][x_columns]
            x = np.array(x)
            x = x.reshape((x.shape[0], 1, x.shape[1]))
            model = Sequential()
            model.add(
                LSTM(
                    len(x_columns),
                    return_sequences=True,
                    input_shape=(x.shape[1], len(x_columns)),
                )
            )
            model.add(LSTM(len(x_columns), input_shape=(x.shape[1], len(x_columns))))
            model.add(Dense(int(self.dense)))
            model.compile(loss="mean_squared_error", optimizer="adam")
            model.load_weights(self.storage.storage["lstm_model"])

            to_predict_data = input_data.loc[len(input_data) - 1 :][x_columns]
            to_predict_data = np.array(to_predict_data)
            to_predict_data = to_predict_data.reshape(
                (to_predict_data.shape[0], 1, to_predict_data.shape[1])
            )
            prediction = model.predict(to_predict_data)[-1][0] + 0.2
            if math.isnan(prediction):
                prediction = 0.0
            if prediction < 0:
                prediction -= 0.2
            else:
                prediction += 0.2

            self.value = prediction

        except Exception as e:
            print("calculate", e)
            self.value = 0.0


