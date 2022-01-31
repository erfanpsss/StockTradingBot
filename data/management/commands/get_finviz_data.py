from django.core.management.base import BaseCommand, CommandParser
from data.models import FinvizDataFile

class Command(BaseCommand): 

    def handle(self, *args, **options):
        try:
            FinvizDataFile.create_finviz_data_automatically()
        except Exception as e:
            print(e)
