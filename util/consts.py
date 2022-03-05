
from django.db import models

class TradeStatusList(models.TextChoices):
    PENDING_SUBMIT = "PendingSubmit"
    PENDING_CANCEL = "PendingCancel"
    PRE_SUBMITTED = "PreSubmitted"
    CANCELLED = "Cancelled"
    SUBMITTED = "Submitted"
    FILLED = "Filled"
    INACTIVE = "Inactive"
    FAILED = "Failed"
    

UPDATE_EXCLUDED_TRADE_STATUS = (
    TradeStatusList.CANCELLED.value,
    TradeStatusList.FILLED.value,
    TradeStatusList.INACTIVE.value,
    TradeStatusList.FAILED.value,
)

class TradeType(models.TextChoices):
    OPEN = "Open"
    CLOSE = "Close"

class PositionType(models.TextChoices):
    BUY = "buy"
    SELL = "sell"

class OrderType(models.TextChoices):
    LMT = "LMT"
    MKT = "MKT"
    STP = "STP"
    STOP_LIMIT = "STOP_LIMIT"
    MIDPRICE = "MIDPRICE"
