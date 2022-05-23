
BROKERS_LIST_CHOICES = (
    ("InteractiveBrokers", "InteractiveBrokers"),
    ("IG", "IG"),
)

CURRENCY_LIST_CHOICES = (
    ("AUD", "AUD"),
    ("USD", "USD"),
)

POSITION_TYPES = (
    ("buy", "buy"),
    ("sell", "sell"),
)
CREATOR_CHOICES = (
    ("Manual", "Manual"),
    ("Automatic", "Automatic"),
)
TRADE_TYPES_CHOICES = (
    ("Open", "Open"),
    ("Close", "Close")
)

TRADE_STATUS_CHOICES = (
    ("PendingSubmit", "PendingSubmit"),
    ("PendingCancel", "PendingCancel"),
    ("PreSubmitted", "PreSubmitted"),
    ("Cancelled", "Cancelled"),
    ("Submitted", "Submitted"),
    ("Filled", "Filled"),
    ("Inactive", "Inactive"),
    ("Failed", "Failed"),
)

ORDER_TYPE_CHOICES = (
    ("LMT", "LMT"),
    ("MKT", "MKT"),
    ("STP", "STP"),
    ("STOP_LIMIT", "STOP_LIMIT"),
    ("MIDPRICE", "MIDPRICE"),
)
