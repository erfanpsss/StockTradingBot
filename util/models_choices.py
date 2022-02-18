
BROKERS_LIST_CHOICES = (
    ("InteractiveBrokers", "InteractiveBrokers"),
    ("FakeBroker", "FakeBroker"),
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
