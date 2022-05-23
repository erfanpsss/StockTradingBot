import yfinance as yf
import pandas as pd
from data.models import Data, Symbol, Timeframe
import pytz
import importlib
import datetime
import uuid
from abc import ABC, abstractmethod, abstractproperty
import requests
import json
import time
from util.consts import TradeStatusList
from util.models_choices import *
from util.consts import *


class BrokerEngine:

    def __init__(self, is_sandbox: bool, public_key: str, secret_key: str, broker: str, account_id: str, broker_instance: "Broker", *args, **kwargs):
        self.broker_instance = broker_instance
        self.is_sandbox = is_sandbox
        self.public_key = public_key
        self.secret_key = secret_key
        self.account_id = account_id
        self.broker = broker
        self.args = args
        self.kwargs = kwargs
        self.broker_processor = self.get_broker_processor()

    def get_broker_processor(self) -> "BrokerProcessor":
        module = importlib.import_module("broker.brokers")
        broker_processor: BrokerProcessor = getattr(module, self.broker)
        return broker_processor(self.is_sandbox, self.public_key, self.secret_key, self.account_id, self.broker_instance, self.args, self.kwargs)


class BrokerProcessor(ABC):
    def __init__(self, is_sandbox, public_key, secret_key, account_id, broker_instance, *args, **kwargs):
        self.is_sandbox = is_sandbox
        self.public_key = public_key
        self.secret_key = secret_key
        self.account_id = account_id
        self.broker_instance = broker_instance

    @abstractmethod
    def connect(self):
        pass

    @abstractproperty
    def account_info(self):
        pass

    @abstractmethod
    def keep_auth_alive(self):
        pass

    @abstractproperty
    def balance(self):
        pass

    @abstractproperty
    def equity(self):
        pass

    @abstractproperty
    def used_margin(self):
        pass

    @abstractmethod
    def open_position(self, *args, **kwargs):
        pass

    @abstractmethod
    def close_position(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_data(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_order(self, *args, **kwargs):
        pass

    @abstractmethod
    def cancel_order(self, *args, **kwargs):
        pass

    @abstractmethod
    def order_status(self, *args, **kwargs):
        pass


class InteractiveBrokers(BrokerProcessor):
    BASE_URL = "http://localhost:5000/v1/api/"
    SSO_VALIDATE_URL = "sso/validate"
    PING_SERVER_URL = "tickle"
    ACCOUNT_INFO_URL = "portfolio/accounts"
    ACCOUNT_BALANCE_INFO_URL = "portfolio/{account_id}/summary"
    AUTH_STATUS_URL = "iserver/auth/status"
    REAUTH_URL = "iserver/reauthenticate"
    SYMBOL_INFO_URL = "iserver/secdef/search"
    PORTFOLIO_POSITIONS = "portfolio/{account_id}/positions/{page_id}"
    PLACE_ORDER_URL = "iserver/account/{account_id}/orders"
    LIST_ORDERS_URL = "iserver/account/orders"
    CANCEL_ORDER_URL = "iserver/account/{account_id}/order/{order_id}"
    PLACE_ORDER_REPLY_URL = "iserver/reply/{reply_id}"
    ORDER_STATUS_URL = "iserver/account/order/status/{order_id}"
    ORDER_STATUS_MAP = {
        "PendingSubmit": TradeStatusList.PENDING_SUBMIT.value,
        "PendingCancel": TradeStatusList.PENDING_CANCEL.value,
        "PreSubmitted": TradeStatusList.PRE_SUBMITTED.value,
        "Cancelled": TradeStatusList.CANCELLED.value,
        "Submitted": TradeStatusList.SUBMITTED.value,
        "Filled": TradeStatusList.FILLED.value,
        "Inactive": TradeStatusList.INACTIVE.value,
    }

    WAIT_AFTER_REAUTH = 10
    MAX_REAUTH_RETRY = 10

    def broker_auth_request(self, method, url, headers=None, data=None):
        headers = {"Content-Type": "application/json"}
        if method.lower() == "post":
            return json.loads(requests.post(self.BASE_URL + url, data=json.dumps(data), headers=headers).content)
        if method.lower() == "delete":
            return json.loads(requests.delete(self.BASE_URL + url, headers=headers).content)
        return json.loads(requests.get(self.BASE_URL + url, headers=headers).content)

    def broker_request(self, method, url, headers=None, data=None):
        headers = {"Content-Type": "application/json"}
        if method.lower() == "post":
            res = requests.post(self.BASE_URL + url,
                                data=json.dumps(data), headers=headers).content
            return json.loads(res)
        if method.lower() == "delete":
            res = requests.delete(self.BASE_URL + url, headers=headers).content
            return json.loads(res)
        res = requests.get(self.BASE_URL + url, headers=headers).content
        return json.loads(res)

    @property
    def auth_status(self):
        return self.broker_auth_request("post", self.AUTH_STATUS_URL)

    @property
    def is_authenticated(self):
        return self.auth_status.get("authenticated") == True

    def keep_auth_alive(self):
        return self.broker_auth_request("post", self.PING_SERVER_URL)

    def reauthenticate(self):
        return self.broker_auth_request("post", self.REAUTH_URL)

    def get_symbol_info(self, symbol_name):
        payload = {
            "symbol": symbol_name,
            "name": True,
            "secType": "STK"
        }
        return self.broker_request("post", self.SYMBOL_INFO_URL, data=payload)

    def get_symbol_conid(self, symbol_name):
        return self.get_symbol_info(symbol_name)[0].get("conid")

    def connect(self):
        if self.is_authenticated:
            return True
        self.reauthenticate()
        for counter in range(1, self.MAX_REAUTH_RETRY + 1):
            print("checking connection... ", counter)
            if self.is_authenticated:
                return True
            time.sleep(self.WAIT_AFTER_REAUTH)
        return False

    def _account_info(self):
        return self.broker_request("get", self.ACCOUNT_INFO_URL)

    @property
    def account_info(self):
        account_info = self._account_info()[0]
        balance_info = self.account_balance_info()
        account_info.update(balance_info)
        account_info.update(
            {
                "balance": account_info.get("availablefunds", {}).get("amount", ""),
                "equity": account_info.get("availablefunds", {}).get("amount", ""),
                "buying_power": account_info.get("buyingpower", {}).get("amount", "")
            }
        )
        return account_info

    def account_balance_info(self):
        info = self.broker_request(
            "get", self.ACCOUNT_BALANCE_INFO_URL.format(account_id=self.account_id))
        return info

    @property
    def balance(self):
        return self.account_balance_info().get("availablefunds", {}).get("amount", "")

    @property
    def equity(self):
        return self.account_balance_info().get("availablefunds", {}).get("amount", "")

    @property
    def used_margin(self):
        pass

    def _open_position(self, *args, **kwargs):
        """Place new market order

        Returns:
            dict: the returned format:

                [{"order_id":"1798885536","local_order_id":"test_1","order_status":"PendingSubmit","encrypt_message":"1"}]
        """
        payload = {
            "orders": [
                {
                    "acctId": self.account_id,
                    "conid": self.get_symbol_conid(kwargs.get("symbol")),
                    "conidex": None,
                    "secType": "STK",
                    "cOID": kwargs.get("cOID"),
                    "parentId": kwargs.get("parent_id"),
                    "orderType": kwargs.get("order_type", "MKT"),
                    "listingExchange": "SMART",
                    "isSingleGroup": True,
                    "outsideRTH": False,
                    "price": kwargs.get("price", None),
                    "auxPrice": None,
                    "side": kwargs.get("position_type").upper(),
                    "ticker": kwargs.get("symbol").upper(),
                    "tif": "GTC",
                    "referrer": "test",
                    "quantity": int(kwargs.get("quantity")),
                    "cashQty": None,
                    "fxQty": None,
                    "useAdaptive": False,
                    "isCcyConv": False,
                    "allocationMethod": "AvailableEquity",
                    "strategy": None,
                    "strategyParameters": {},
                },
            ],
        }
        print("Open position payload: ", payload)
        return self.broker_request("post", self.PLACE_ORDER_URL.format(account_id=self.account_id), data=payload)

    def reply_place_order(self, reply_id):
        payload = {
            "confirmed": True
        }
        return self.broker_request("post", self.PLACE_ORDER_REPLY_URL.format(reply_id=reply_id), data=payload)

    def open_position(self, *args, **kwargs):
        print("Opening trade...")
        position = self._open_position(*args, **kwargs)[0]
        reply_id = position.get("id")
        if reply_id:
            position = self.reply_place_order(reply_id)[0]
            return position.get("order_id"), self.ORDER_STATUS_MAP.get(position.get("order_status"))
        return position.get("order_id"), self.ORDER_STATUS_MAP.get(position.get("order_status"))

    def cancel_order(self, *args, **kwargs):
        return self.broker_request("delete", self.CANCEL_ORDER_URL.format(account_id=self.account_id, order_id=kwargs.get("order_id")))

    def _positions(self, *args, **kwargs):
        """Return orders

        Returns:
            dict: the returned format:
                {
                    "orders":[
                        {"acct":"DU4677076","conidex":"459468268","conid":459468268,"orderId":1275658265,"cashCcy":"USD","sizeAndFills":"0/10","orderDesc":"Buy 10 Market DAY","description1":"PUBM","ticker":"PUBM","secType":"STK","listingExchange":"NASDAQ.NMS","remainingQuantity":10.0,"filledQuantity":0.0,"companyName":"PUBMATIC INC-CLASS A","status":"PreSubmitted","origOrderType":"MARKET","supportsTaxOpt":"1","lastExecutionTime":"220212082221","orderType":"Market","bgColor":"#FFFFFF","fgColor":"#997EE5","order_ref":"54353149","timeInForce":"CLOSE","lastExecutionTime_r":1644654141000,"side":"BUY"},
                        {"acct":"DU4677076","conidex":"265598","conid":265598,"orderId":1082609734,"cashCcy":"USD","sizeAndFills":"0/1","orderDesc":"Buy 1 Market GTC","description1":"AAPL","ticker":"AAPL","secType":"STK","listingExchange":"NASDAQ.NMS","remainingQuantity":1.0,"filledQuantity":0.0,"companyName":"APPLE INC","status":"PreSubmitted","origOrderType":"MARKET","supportsTaxOpt":"1","lastExecutionTime":"220213075823","orderType":"Market","bgColor":"#FFFFFF","fgColor":"#997EE5","order_ref":"test_1","timeInForce":"GTC","lastExecutionTime_r":1644739103000,"side":"BUY"},
                        {"acct":"DU4677076","conidex":"265598","conid":265598,"orderId":1798885536,"cashCcy":"USD","sizeAndFills":"0/1","orderDesc":"Buy 1 Market GTC","description1":"AAPL","ticker":"AAPL","secType":"STK","listingExchange":"NASDAQ.NMS","remainingQuantity":1.0,"filledQuantity":0.0,"companyName":"APPLE INC","status":"PendingSubmit","origOrderType":"MARKET","supportsTaxOpt":"1","lastExecutionTime":"220213235759","orderType":"Market","bgColor":"#000000","fgColor":"#3399CC","order_ref":"test_1","timeInForce":"GTC","lastExecutionTime_r":1644796679000,"side":"BUY"}
                    ],
                    "snapshot":true
                }'
        """
        return self.broker_request("get", self.LIST_ORDERS_URL)

    def positions(self, *args, **kwargs):
        positions = self.broker_request(
            "get", self.LIST_ORDERS_URL).get("orders")
        data = []
        for position in positions:
            data.append({
                "quantity": position.get("sizeAndFills").split("/")[-1],
                "symbol": position.get("ticker"),
                "position_type": position.get("side"),
                "position_id": position.get("orderId"),
            })
        return data

    def _order_status(self, *args, **kwargs):
        return self.broker_request("get", self.ORDER_STATUS_URL.format(order_id=kwargs.get("order_id")))

    def order_status(self, *args, **kwargs):
        """Return order status

        Returns:
            str: order status from the following list:
                PendingSubmit: Indicates the order was sent, but confirmation has not been received that it has been received by the destination.
                PendingCancel: Indicates that a request has been sent to cancel an order but confirmation has not been received of its cancellation.
                PreSubmitted: Indicates that a simulated order type has been accepted by the IBKR system and that this order has yet to be elected.
                Cancelled: Indicates that the balance of the order has been confirmed cancelled by the IB system.
                Submitted: Indicates that the order has been accepted at the order destination and is working.
                Filled: Indicates that the order has been completely filled.
                Inactive: Indicates the order is not working, for instance if the order was invalid and triggered an error message,
        """

        return self._order_status(*args, **kwargs).get("order_status")

    def close_position(self, *args, **kwargs):
        order_status = self._order_status(*args, **kwargs)
        if order_status.get("order_status") in ("Filled"):
            kwargs["symbol"] = order_status.get("symbol")
            kwargs["position_type"] = "sell"
            kwargs["quantity"] = order_status.get("total_size")
            return self.open_position(*args, **kwargs)
        return self.cancel_order(*args, **kwargs)

    def get_data(self, *args, **kwargs):
        pass

    def create_order(self, *args, **kwargs):
        pass

    def cancel_order(self, *args, **kwargs):
        pass


class FakeBroker(BrokerProcessor):
    ACCOUNT_INFO_FILE_NAME: str = "fake_broke_account_info.csv"
    INITIAL_BALANCE: float = 1000.0

    def __init__(self, is_sandbox, public_key, secret_key, *args, **kwargs):
        super().__init__(is_sandbox, public_key, secret_key, *args, **kwargs)
        self.intial_balance = kwargs.get("balance") or self.INITIAL_BALANCE
        self.setup_account()

    def setup_account(self):
        if not self.storage.storage.get("account_info"):
            self.storage.storage = {
                "account_info": {
                    "balance": self.intial_balance,
                    "equity": self.intial_balance,
                    "used_margin": 0.0
                }
            }
            self.storage.save()

    @property
    def account_info(self) -> dict:
        return self.storage.storage.get("account_info")

    @property
    def balance(self) -> float:
        return self.account_info.get("balance")

    @property
    def equity(self) -> float:
        return self.account_info.get("equity")

    @property
    def used_margin(self) -> float:
        return self.account_info.get("used_margin")

    def open_position(self, *args, **kwargs):
        position_size: float = kwargs.get("position_size")
        position_stop_loss: float = kwargs.get("stop_loss")
        position_limit: float = kwargs.get("limit")
        symbol: Symbol = kwargs.get("symbol")
        position_type: str = kwargs.get("position_type")
        trade_datetime: datetime.datetime = kwargs.get("trade_datetime")
        trade_price = datetime.datetime = kwargs.get("trade_price")
        executor: str = kwargs.get("executor")
        trade_type: str = "open"
        position_id: str = (uuid.uuid4())
        broker: str = "FakeBroker"

        data: dict = {
            "position_size": position_size,
            "position_stop_loss": position_stop_loss,
            "position_limit": position_limit,
            "symbol": symbol,
            "position_type": position_type,
            "trade_datetime": trade_datetime,
            "trade_price": trade_price,
            "trade_type": trade_type,
            "position_id": position_id,
            "broker": broker,
            "executor": executor
        }

        return position_id

    def close_position(self, *args, **kwargs):
        position_size: float = kwargs.get("position_size")
        position_stop_loss: float = kwargs.get("stop_loss")
        position_limit: float = kwargs.get("limit")
        symbol: Symbol = kwargs.get("symbol")
        position_type: str = kwargs.get("position_type")
        trade_datetime: datetime.datetime = kwargs.get("trade_datetime")
        trade_price = datetime.datetime = kwargs.get("trade_price")
        executor: str = kwargs.get("executor")
        parent_trade: "Trade" = kwargs.get("parent_trade")
        trade_type: str = "close"
        position_id: str = (uuid.uuid4())
        broker: str = "FakeBroker"

        data: dict = {
            "position_size": position_size,
            "position_stop_loss": position_stop_loss,
            "position_limit": position_limit,
            "symbol": symbol,
            "position_type": position_type,
            "trade_datetime": trade_datetime,
            "trade_price": trade_price,
            "trade_type": trade_type,
            "position_id": position_id,
            "broker": broker,
            "executor": executor,
            "parent_trade": parent_trade
        }

        return position_id

    def get_data(self, *args, **kwargs):
        pass


class IG(BrokerProcessor):
    BASE_URL_LIVE = "https://api.ig.com/gateway/deal/"
    BASE_URL_SANDBOX = "https://demo-api.ig.com/gateway/deal/"
    SESSION = "session"
    SYMBOL_INFO_URL = "markets"
    PING_SERVER_URL = "tickle"
    ACCOUNT_INFO_URL = "accounts"
    PLACE_ORDER_URL = "positions/otc"
    ORDER_STATUS_MAP = {
        "PendingSubmit": TradeStatusList.PENDING_SUBMIT.value,
        "PendingCancel": TradeStatusList.PENDING_CANCEL.value,
        "PreSubmitted": TradeStatusList.PRE_SUBMITTED.value,
        "Cancelled": TradeStatusList.CANCELLED.value,
        "Submitted": TradeStatusList.SUBMITTED.value,
        "Filled": TradeStatusList.FILLED.value,
        "Inactive": TradeStatusList.INACTIVE.value,
    }

    WAIT_AFTER_REAUTH = 10
    MAX_REAUTH_RETRY = 10
    ORDER_TYPE_MAPPING = {
        "MKT": "MARKET"
    }

    @property
    def BASE_URL(self):
        if self.is_sandbox:
            return self.BASE_URL_SANDBOX
        return self.BASE_URL_LIVE

    def broker_auth_request(self, method, url, headers=None, data=None):
        raw_headers = {
            "X-IG-API-KEY": self.broker_instance.api_key,
            "Accept": "application/json; charset=UTF-8",
            "Content-Type": "application/json; charset=UTF-8",
            "Version": "2"
        }
        if headers:
            raw_headers.update(headers)
        if method.lower() == "post":
            return requests.post(self.BASE_URL + url, data=json.dumps(data), headers=raw_headers)
        if method.lower() == "delete":
            return requests.delete(self.BASE_URL + url, headers=raw_headers)
        return requests.get(self.BASE_URL + url, headers=raw_headers)

    def broker_request(self, method, url, headers=None, data=None, params=None):
        raw_headers = {
            "X-IG-API-KEY": self.broker_instance.api_key,
            "Accept": "application/json; charset=UTF-8",
            "Content-Type": "application/json; charset=UTF-8",
            "Version": "1",
            "X-SECURITY-TOKEN": self.broker_instance.storage.get("X-SECURITY-TOKEN", ""),
            "CST": self.broker_instance.storage.get("CST", "")
        }
        if headers:
            raw_headers.update(headers)
        if method.lower() == "post":
            res = requests.post(self.BASE_URL + url,
                                data=json.dumps(data), headers=raw_headers, params=params).content
            return json.loads(res)
        if method.lower() == "delete":
            res = requests.delete(self.BASE_URL + url,
                                  headers=raw_headers, params=params).content
            return json.loads(res)
        res = requests.get(self.BASE_URL + url,
                           headers=raw_headers, params=params).content
        return json.loads(res)

    def authenticate(self):
        response = self.broker_auth_request("post", self.SESSION, data={
                                            "identifier": self.broker_instance.username, "password": self.broker_instance.password, "encryptedPassword": None})
        self.broker_instance.add_or_update_storage(
            "X-SECURITY-TOKEN", response.headers.get("X-SECURITY-TOKEN"))
        self.broker_instance.add_or_update_storage(
            "CST", response.headers.get("CST"))

    def _auth_status(self):
        return self.broker_request("get", self.SESSION, headers={"Version": "1"})

    @property
    def auth_status(self):
        return self._auth_status()

    @property
    def is_authenticated(self):
        try:
            return self.auth_status.get("accountId") == self.account_id
        except Exception as e:
            print("is_authenticated", e)
            return False

    def keep_auth_alive(self):
        return None

    def reauthenticate(self):
        return self.authenticate()

    def connect(self):
        if self.is_authenticated:
            return True
        self.reauthenticate()
        for counter in range(1, self.MAX_REAUTH_RETRY + 1):
            print("checking connection... ", counter)
            if self.is_authenticated:
                return True
            time.sleep(self.WAIT_AFTER_REAUTH)
        return False

    def _account_info(self):
        return self.broker_request("get", self.ACCOUNT_INFO_URL, headers={"Version": "1"})

    @property
    def account_info(self):
        accounts_info = self._account_info().get("accounts", [])
        current_account_info = {}
        for account in accounts_info:
            if account.get("accountId") == self.account_id:
                current_account_info = account
                break
        current_account_info.update(
            {
                "balance": current_account_info.get("balance", {}).get("balance", ""),
                "equity": current_account_info.get("balance", {}).get("available", ""),
                "buying_power": current_account_info.get("balance", {}).get("available", "")
            }
        )
        return current_account_info

    @property
    def balance(self):
        return self.account_info.get("balance", {}).get("amount", "")

    @property
    def equity(self):
        return self.account_info.get("equity", {}).get("amount", "")

    @property
    def used_margin(self):
        pass

    def get_symbol_info(self, symbol_name):
        params = {
            "searchTerm": symbol_name,
        }
        return self.broker_request("get", self.SYMBOL_INFO_URL, params=params)

    def get_symbol_epic(self, symbol_name):
        return self.get_symbol_info(symbol_name).get("markets", [{"epic": None}])[0].get("epic")

    def _open_position(self, *args, **kwargs):
        """Place new market order

        Returns:
            dict: the returned format:
        """
        payload = {
            "currencyCode ": self.broker_instance.currency,
            "dealReference": kwargs.get("cOID"),
            "direction ": kwargs.get("position_type").upper(),
            "epic": self.get_symbol_epic(kwargs.get("symbol")),
            "orderType": self.ORDER_TYPE_MAPPING.get(kwargs.get("order_type", "MKT")),
            "timeInForce": "EXECUTE_AND_ELIMINATE",
            "size": kwargs.get("quantity"),
            "guaranteedStop": "false",
            "expiry": "-",
            "forceOpen": "false",
            "stopLevel": None,
            "stopDistance": None,
            "trailingStop": None,
            "timeInForce": None,
            "level": None,
            "trailingStopIncrement": None,
            "limitLevel": None,
            "limitDistance": None,
            "quoteId": None,
        }
        print("Open position payload: ", payload)
        return self.broker_request("post", self.PLACE_ORDER_URL, data=payload)

    def _close_position(self, *args, **kwargs):
        """Close open position

        Returns:
            dict: the returned format:

        """
        payload = {
            "dealid ": kwargs.get("parent_trade_position_id"),
            "direction ": kwargs.get("position_type").upper(),
            "orderType": self.ORDER_TYPE_MAPPING.get(kwargs.get("order_type", "MKT")),
            "timeInForce": "EXECUTE_AND_ELIMINATE",
            "size": kwargs.get("quantity"),
        }
        print("Close position payload: ", payload)
        return self.broker_request("delete", self.PLACE_ORDER_URL, data=payload)

    def open_position(self, *args, **kwargs):
        print("Opening trade...")
        if kwargs.get("trade_type") == TradeType.OPEN.value:
            position = self._open_position(*args, **kwargs)
        else:
            position = self._close_position(*args, **kwargs)
        return position.get("dealReference"), TradeStatusList.FILLED.value if position.get("dealReference") else TradeStatusList.FAILED.value

    def _positions(self, *args, **kwargs):
        """Return orders

        Returns:

        """
        return self.broker_request("get", self.LIST_POSITIONS_URL)

    def positions(self, *args, **kwargs):
        positions = self._positions(*args, **kwargs)
        data = []
        for position in positions:
            data.append({
                "quantity": position.get('position', {}).get("size"),
                "symbol": position.get('market', {}).get("epic"),
                "position_type": position.get('position', {}).get("direction"),
                "dealReference": position.get("dealId"),
            })
        return data

    def close_position(self, *args, **kwargs):
        position = self._close_position(*args, **kwargs)
        return position.get("dealReference"), TradeStatusList.FILLED.value if position.get("dealReference") else TradeStatusList.FAILED.value

    def get_data(self, *args, **kwargs):
        pass

    def order_status(self, *args, **kwargs):
        """Return order status

        """

        return []

    def create_order(self, *args, **kwargs):
        pass

    def cancel_order(self, *args, **kwargs):
        pass
