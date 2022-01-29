from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
import os
from multiprocessing import Process

def run_cmd_command(commands):
    os.system(commands)


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
            p = Process(target=run_cmd_command, args=(commands,))
            p.start()
            p.join()
        except Exception as e:
            print(e)
