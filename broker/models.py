from email.policy import default
from django.db import models
from data.models import Symbol
import importlib
from django.contrib.auth.models import User
import datetime
import uuid
from.brokers import BrokerEngine
from util.models_choices import *


class Broker(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_broker")
    name = models.CharField(max_length=50)
    account_id = models.CharField(max_length=255, blank = True, null = True)
    is_sandbox = models.BooleanField(default=True)
    public_key = models.CharField(max_length=255, blank = True, null = True)
    secret_key = models.CharField(max_length=255, blank = True, null = True)
    broker_class = models.CharField(max_length=50, choices=BROKERS_LIST_CHOICES)
    storage = models.JSONField(default=dict, blank = True, null = True)
    balance = models.FloatField(default=0.0)
    equity = models.FloatField(default=0.0)
    buying_power = models.FloatField(default=0.0)
    used_margin = models.FloatField(default=0.0)
    connected = models.BooleanField(default=False)
    error = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "Broker"
        verbose_name_plural = "Brokers"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.setup()

    def setup(self):
        pass

    def run_scheduled_calls(self):
        print("Updating connection")
        self.connection_update()
        print("Updating account info")
        self.refresh_account_info()
    
    @property
    def broker(self):
        return BrokerEngine(self.is_sandbox, self.public_key, self.secret_key, self.broker_class, self.account_id).broker_processor

    def connection_update(self):
        try:
            self.connected = self.broker.is_authenticated
            self.save()
            connection = self.broker.connect()
            self.connected = connection
            self.error = ""
            self.save()
            return connection
        except Exception as e:
            print("connection_update", e)
            self.connected = False
            self.error = str(e)
            self.save()
            return False

    def refresh_account_info(self):
        try:
            account_info = self.broker.account_info
            self.balance = account_info.get("balance")
            self.equity = account_info.get("equity")
            self.buying_power = account_info.get("buying_power")
            current_storage = self.storage
            current_storage["account_balance_info"] = account_info
            self.storage = current_storage
            self.save()
        except Exception as e:
            print("refresh_account_info", e)

    @property
    def account_info(self):
        return f"Balance: {self.balance}, equity: {self.equity}"
        


    

        

