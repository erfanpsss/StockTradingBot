from django.core.management.base import BaseCommand, CommandParser
from runner.runner import Runner

class Command(BaseCommand): 

    def handle(self, *args, **options):
        try:
            runner = Runner()
            runner.run()
        except Exception as e:
            print(e)
