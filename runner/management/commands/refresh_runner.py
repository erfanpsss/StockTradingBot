from django.core.management.base import BaseCommand, CommandParser
from runner.models import RunnerStatus

class Command(BaseCommand): 

    def handle(self, *args, **options):
        try:
            RunnerStatus.objects.first().handle_start_runner()
        except Exception as e:
            print(e)
