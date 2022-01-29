from django.core.management.base import BaseCommand, CommandParser
from provider.receivers import YahooFinance

class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--symbol")
        parser.add_argument("--timeframe")
        parser.add_argument("--period", default=None)  

    def handle(self, *args, **options):
        try:
            symbol = options["symbol"]
            timeframe = options["timeframe"]
            period = options["period"]
            provider = YahooFinance(symbol = symbol, timeframe = timeframe, period = period)
            provider.run()
        except Exception as e:
            print(e)
