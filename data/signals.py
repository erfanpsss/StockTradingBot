import datetime
import importlib
import json
from threading import Thread

from django.conf import settings
from django.db import transaction
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
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Data


def default_json(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


def calculate_all_indicators(price):
    for indicator in Data.get_available_indicator_configuration():
        try:
            with transaction.atomic():
                module = importlib.import_module("indicator.models")
                indicator_class = getattr(module, indicator["class"])
                temp_obj = indicator_class(**indicator["args"])
                temp_obj.price_id = price
                temp_obj.pre_save()
                temp_obj.save()
        except Exception as e:
            pass


@receiver(post_save, sender=Data)
def calculate_indicators(sender, instance, created=False, **kwargs):
    calculate_all_indicators(instance)
