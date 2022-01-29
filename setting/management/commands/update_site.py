from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
import os

class Command(BaseCommand): 

    def handle(self, *args, **options):
        try:

            commands = f"""
            cd {str(settings.BASE_DIR)}
            git checkout main
            git fetch
            git pull
            git checkout {settings.GIT_BRANCH_NAME}
            git merge main
            git push
            """

            os.system(commands)
        except Exception as e:
            print(e)
