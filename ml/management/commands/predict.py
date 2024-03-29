from django.core.management.base import BaseCommand, CommandParser
from data.models import FinvizDataFile
from keras import Input
from keras.layers import (
    LSTM,
    Bidirectional,
    Dense,
    RepeatVector,
    Dropout,
    TimeDistributed,
)
from joblib import load
from django.core.files.storage import default_storage
from sklearn.model_selection import GridSearchCV
import xgboost as xgb
from tensorflow.keras.models import load_model
from keras.models import Sequential
from keras.utils.generic_utils import default
from numpy.lib.arraysetops import unique
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
from tensorflow.keras.models import Sequential
from django.core.files.base import ContentFile
from tensorflow.keras.layers import Dense
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPClassifier, MLPRegressor
from data.models import IbdData, FinvizInsiderData
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import pickle
from sklearn.metrics import mean_squared_error
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from django.db.models import (
    Q,
    F,
    Subquery,
    OuterRef,
    Count,
    Sum,
    Avg,
    Max,
    Min,
)
from django.db.models import Sum, Count, Avg, F, FloatField, Case, When
from django.db.models.functions import Cast
from ml.choices import ModelType
from ml.models import MlModels
from data.models import FinvizSectorData
from ml.constants import STOCK_ML_FEATURES
from sklearn.preprocessing import LabelEncoder


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--model_type", type=str)
        parser.add_argument("--symbol", type=str)

    def handle(self, *args, **options):
        print("Model:", options["model_type"])
        try:
            features = STOCK_ML_FEATURES

            data_raw = IbdData.objects.filter(
                date__lt=datetime.date(2022, 3, 1),
                price__isnull=False,
                company__isnull=False,
            ).order_by("date")
            insider_data_raw = FinvizInsiderData.objects.filter(
                date__lt=datetime.date(2022, 3, 1)
            ).order_by("date")
            insider_trades_subquery = insider_data_raw.filter(
                symbol=OuterRef("symbol"), date=OuterRef("date")
            ).values("symbol")

            number_of_insider_trades = Subquery(
                insider_trades_subquery.annotate(
                    count=Count("transaction")
                ).values("count"),
                output_field=FloatField(),
            )

            # Get the subquery for total value of insider trades
            total_value_of_insider_trades = Subquery(
                insider_trades_subquery.annotate(
                    total_value=Sum("shares")
                ).values("total_value"),
                output_field=FloatField(),
            )

            # Get the subquery for percentage of 'Buy' transactions
            percentage_of_insider_buy_trades = Subquery(
                insider_trades_subquery.annotate(
                    percentage=Cast(
                        Sum(
                            Case(
                                When(transaction="Buy", then=1),
                                default=0,
                                output_field=FloatField(),
                            )
                        )
                        / Count("transaction")
                        * 100,
                        FloatField(),
                    )
                ).values("percentage"),
                output_field=FloatField(),
            )
            # Get the subquery for percentage of 'Sale' transactions
            percentage_of_insider_sale_trades = Subquery(
                insider_trades_subquery.annotate(
                    percentage=Cast(
                        Sum(
                            Case(
                                When(transaction="Sale", then=1),
                                default=0,
                                output_field=FloatField(),
                            )
                        )
                        / Count("transaction")
                        * 100,
                        FloatField(),
                    )
                ).values("percentage"),
                output_field=FloatField(),
            )

            sector_market_cap = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("market_cap")
            )
            sector_pe = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("pe")
            )
            sector_forward_pe = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("forward_pe")
            )
            sector_peg = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("peg")
            )
            sector_ps = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("ps")
            )
            sector_pb = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("pb")
            )
            sector_pc = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("pc")
            )
            sector_p_free_cash_flow = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("p_free_cash_flow")
            )
            sector_dividend_yield_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("dividend_yield_percentage")
            )
            sector_eps_growth_past_5_years_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("eps_growth_past_5_years_percentage")
            )
            sector_eps_growth_next_5_years_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("eps_growth_next_5_years_percentage")
            )
            sector_sales_growth_past_5_years_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("sales_growth_past_5_years_percentage")
            )
            sector_float_short_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("float_short_percentage")
            )
            sector_performance_week_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("performance_week_percentage")
            )
            sector_performance_month_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("performance_month_percentage")
            )
            sector_performance_quarter_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("performance_quarter_percentage")
            )
            sector_performance_half_year_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("performance_half_year_percentage")
            )
            sector_performance_year_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("performance_year_percentage")
            )
            sector_performance_year_to_date_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("performance_year_to_date_percentage")
            )
            sector_analyst_recom = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("analyst_recom")
            )
            sector_average_volume = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("average_volume")
            )
            sector_relative_volume = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("relative_volume")
            )
            sector_change_percentage = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("change_percentage")
            )
            sector_volume = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("volume")
            )
            sector_stocks = Subquery(
                FinvizSectorData.objects.filter(
                    date=OuterRef("date"),
                    sector__name__iexact=OuterRef("sector"),
                ).values("stocks")
            )

            subquery = (
                IbdData.objects.filter(symbol=OuterRef("symbol"))
                .filter(date__lt=OuterRef("date"))
                .order_by("-date")
            )
            data_pre_list = data_raw.annotate(
                previous_price=Subquery(subquery.values("price")[:1]),
                number_of_insider_trades=number_of_insider_trades,
                total_value_of_insider_trades=total_value_of_insider_trades,
                percentage_of_insider_buy_trades=percentage_of_insider_buy_trades,
                percentage_of_insider_sale_trades=percentage_of_insider_sale_trades,
                sector_market_cap=sector_market_cap,
                sector_pe=sector_pe,
                sector_forward_pe=sector_forward_pe,
                sector_peg=sector_peg,
                sector_ps=sector_ps,
                sector_pb=sector_pb,
                sector_pc=sector_pc,
                sector_p_free_cash_flow=sector_p_free_cash_flow,
                sector_dividend_yield_percentage=sector_dividend_yield_percentage,
                sector_eps_growth_past_5_years_percentage=sector_eps_growth_past_5_years_percentage,
                sector_eps_growth_next_5_years_percentage=sector_eps_growth_next_5_years_percentage,
                sector_sales_growth_past_5_years_percentage=sector_sales_growth_past_5_years_percentage,
                sector_float_short_percentage=sector_float_short_percentage,
                sector_performance_week_percentage=sector_performance_week_percentage,
                sector_performance_month_percentage=sector_performance_month_percentage,
                sector_performance_quarter_percentage=sector_performance_quarter_percentage,
                sector_performance_half_year_percentage=sector_performance_half_year_percentage,
                sector_performance_year_percentage=sector_performance_year_percentage,
                sector_performance_year_to_date_percentage=sector_performance_year_to_date_percentage,
                sector_analyst_recom=sector_analyst_recom,
                sector_average_volume=sector_average_volume,
                sector_relative_volume=sector_relative_volume,
                sector_change_percentage=sector_change_percentage,
                sector_volume=sector_volume,
                sector_stocks=sector_stocks,
            )

            data = list(data_pre_list.values(*features))
            df_raw = pd.DataFrame(data)
            le = LabelEncoder()
            df_raw["symbol__name"] = le.fit_transform(df_raw["symbol__name"])
            df_raw["company"] = le.fit_transform(df_raw["company"])
            df_raw["sector"] = le.fit_transform(df_raw["sector"])
            df_raw["industry"] = le.fit_transform(df_raw["industry"])
            df_raw["country"] = le.fit_transform(df_raw["country"])

            print(df_raw.tail())
            df_raw = df_raw.fillna(0)
            df_raw = df_raw[features]
            df_raw["target"] = (
                df_raw["price"] > df_raw["previous_price"]
            ).astype(int)
            df_raw["target"] = df_raw["target"].shift(-1)
            df_raw = df_raw.dropna()

            # Applying normalization
            scaler = MinMaxScaler(feature_range=(0, 1))

            df = pd.DataFrame(
                scaler.fit_transform(df_raw), columns=df_raw.columns
            )
            df["symbol__name"] = df_raw["symbol__name"]
            df["company"] = df_raw["company"]
            df["sector"] = df_raw["sector"]
            df["industry"] = df_raw["industry"]
            df["country"] = df_raw["country"]

            X = df[features]

            # Apply normalization
            scaler = MinMaxScaler(feature_range=(0, 1))
            X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

            if options["model_type"] == ModelType.LogisticRegression.value:
                model = pickle.loads(
                    MlModels.objects.filter(model_type=options["model_type"])
                    .last()
                    .model.file.read()
                )
            elif (
                options["model_type"] == ModelType.RandomForestClassifier.value
            ):
                model = pickle.loads(
                    MlModels.objects.filter(model_type=options["model_type"])
                    .last()
                    .model.file.read()
                )
            elif options["model_type"] == ModelType.NeuralNetwork.value:
                model = load_model(
                    default_storage.path(
                        MlModels.objects.filter(
                            model_type=options["model_type"]
                        )
                        .last()
                        .model.file.name
                    )
                )
            elif options["model_type"] == ModelType.XgBoost.value:
                model = load(
                    default_storage.path(
                        MlModels.objects.filter(
                            model_type=options["model_type"]
                        )
                        .last()
                        .model.file.name
                    )
                )
            elif options["model_type"] == ModelType.DecisionTree.value:
                model = pickle.loads(
                    MlModels.objects.filter(model_type=options["model_type"])
                    .last()
                    .model.file.read()
                )

            symbol = options["symbol"]
            data_raw_test = (
                data_raw.filter(
                    price__isnull=False,
                    company__isnull=False,
                    symbol__name=symbol,
                )
                .order_by("date")
                .annotate(
                    previous_price=Subquery(subquery.values("price")[:1]),
                    number_of_insider_trades=number_of_insider_trades,
                    total_value_of_insider_trades=total_value_of_insider_trades,
                    percentage_of_insider_buy_trades=percentage_of_insider_buy_trades,
                    percentage_of_insider_sale_trades=percentage_of_insider_sale_trades,
                    sector_market_cap=sector_market_cap,
                    sector_pe=sector_pe,
                    sector_forward_pe=sector_forward_pe,
                    sector_peg=sector_peg,
                    sector_ps=sector_ps,
                    sector_pb=sector_pb,
                    sector_pc=sector_pc,
                    sector_p_free_cash_flow=sector_p_free_cash_flow,
                    sector_dividend_yield_percentage=sector_dividend_yield_percentage,
                    sector_eps_growth_past_5_years_percentage=sector_eps_growth_past_5_years_percentage,
                    sector_eps_growth_next_5_years_percentage=sector_eps_growth_next_5_years_percentage,
                    sector_sales_growth_past_5_years_percentage=sector_sales_growth_past_5_years_percentage,
                    sector_float_short_percentage=sector_float_short_percentage,
                    sector_performance_week_percentage=sector_performance_week_percentage,
                    sector_performance_month_percentage=sector_performance_month_percentage,
                    sector_performance_quarter_percentage=sector_performance_quarter_percentage,
                    sector_performance_half_year_percentage=sector_performance_half_year_percentage,
                    sector_performance_year_percentage=sector_performance_year_percentage,
                    sector_performance_year_to_date_percentage=sector_performance_year_to_date_percentage,
                    sector_analyst_recom=sector_analyst_recom,
                    sector_average_volume=sector_average_volume,
                    sector_relative_volume=sector_relative_volume,
                    sector_change_percentage=sector_change_percentage,
                    sector_volume=sector_volume,
                    sector_stocks=sector_stocks,
                )
            )
            test_data = list(data_raw_test.values(*features))[-1:]
            test_df_raw_init = pd.DataFrame(test_data)
            le = LabelEncoder()
            test_df_raw_init["symbol__name"] = le.fit_transform(
                test_df_raw_init["symbol__name"]
            )
            test_df_raw_init["company"] = le.fit_transform(
                test_df_raw_init["company"]
            )
            test_df_raw_init["sector"] = le.fit_transform(
                test_df_raw_init["sector"]
            )
            test_df_raw_init["industry"] = le.fit_transform(
                test_df_raw_init["industry"]
            )
            test_df_raw_init["country"] = le.fit_transform(
                test_df_raw_init["country"]
            )
            test_df_raw = test_df_raw_init.fillna(0)
            test_df_raw = test_df_raw[features]

            # Applying normalization
            scaler = MinMaxScaler(feature_range=(0, 1))
            test_df = pd.DataFrame(
                scaler.fit_transform(test_df_raw), columns=test_df_raw.columns
            )
            test_df["symbol__name"] = test_df_raw_init["symbol__name"]
            test_df["company"] = test_df_raw_init["company"]
            test_df["sector"] = test_df_raw_init["sector"]
            test_df["industry"] = test_df_raw_init["industry"]
            test_df["country"] = test_df_raw_init["country"]

            nx_test = test_df
            pred = model.predict(nx_test)
            if options["model_type"] == ModelType.LogisticRegression.value:
                print("pred_proba all:", model.predict_proba(nx_test))
                print("pred_proba:", model.predict_proba(nx_test)[-1])
            elif (
                options["model_type"] == ModelType.RandomForestClassifier.value
            ):
                print("pred_proba all:", model.predict_proba(nx_test))
                print("pred_proba:", model.predict_proba(nx_test)[-1])
            elif options["model_type"] == ModelType.NeuralNetwork.value:
                print("pred_proba all:", model.predict(nx_test))
                print("pred_proba:", model.predict(nx_test)[-1])
            elif options["model_type"] == ModelType.XgBoost.value:
                print("pred_proba all:", model.predict(nx_test))
                print("pred_proba:", model.predict_proba(nx_test)[-1])
            elif options["model_type"] == ModelType.DecisionTree.value:
                print("pred_proba all:", model.predict(nx_test))
                print("pred_proba:", model.predict_proba(nx_test)[-1])

            print("pred all: ", pred)
            print("pred:", pred[-1])
            print("Symbol:", symbol)
            print(
                "previous price:",
                data_raw_test[data_raw_test.count() - 1].previous_price,
            )
            print(
                "current price:",
                data_raw_test[data_raw_test.count() - 1].price,
            )
            plt.plot(
                list(
                    range(
                        len(
                            list(
                                data_raw.filter(
                                    symbol__name=symbol
                                ).values_list("date", flat=True)
                            )
                        )
                    )
                ),
                list(
                    data_raw.filter(symbol__name=symbol).values_list(
                        "price", flat=True
                    )
                ),
            )
            plt.show()

        except Exception as e:
            print(11111, e)
