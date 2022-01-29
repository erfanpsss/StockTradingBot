from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
import os
from multiprocessing import Process

def run_cmd_command(commands):
    os.system(f'cmd /k "{commands}"')

class Command(BaseCommand): 

    def handle(self, *args, **options):
        try:

            commands = (
                f"cd {str(settings.BASE_DIR)} &"
                f"git checkout main &"
                f"git fetch &"
                f"git pull &"
                f"git checkout {settings.GIT_BRANCH_NAME} &"
                f"git merge main &"
                f"git push"
            )
            p = Process(target=run_cmd_command, args=(commands,))
            p.start()
        except Exception as e:
            print(e)
