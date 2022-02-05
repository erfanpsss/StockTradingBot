from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
import os
from multiprocessing import Process
import sys

def get_pid(server_process_output):
    pid = []
    server_process_output = server_process_output.replace("\n", "")
    for l in range(-1, -len(server_process_output)-1, -1):
        if server_process_output[l] in [" "]:break
        pid.append(server_process_output[l])
    pid.reverse()
    pid = "".join(pid)
    return pid


def run_cmd_command(base_dir, git_branch, python_exe, server_post):
    import django
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)

    os.environ["DJANGO_SETTINGS_MODULE"] = "stocktrading.settings"
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "stocktrading.settings",
    )
    django.setup()
    from runner.models import RunnerStatus

    commands = (
        f"cd {base_dir} &"
        f"git checkout main &"
        f"git fetch &"
        f"git pull &"
        f"git checkout {git_branch} &"
        f"git merge main &"
        f"git push &"
        f"{python_exe} -m pip install -r requirements.txt &"
        f"{python_exe} manage.py migrate"
    )
    os.system(f'{commands}')
    os.system(f'netstat -ano | findstr 127.0.0.1:{server_post} > tmp_server_pid')
    server_process_outputs = open('tmp_server_pid', 'r').readlines()
    os.remove("tmp_server_pid")

    for server_process_output in server_process_outputs:
        pid = get_pid(server_process_output)
        if pid == "0":
            continue
        stop_server_command = f"taskkill /PID {pid} /F"
        os.system(f'{stop_server_command}')
        
    RunnerStatus.objects.first().handle_start_runner()
    run_server_command = (
        f"cd {base_dir} &"
        f"{python_exe} manage.py runserver 127.0.0.1:{server_post}"
    )
    os.system(f'{run_server_command}')

class Command(BaseCommand): 

    def handle(self, *args, **options):
        try:
            p = Process(target=run_cmd_command, args=(str(settings.BASE_DIR), settings.GIT_BRANCH_NAME, settings.PYTHON_EXE, settings.SERVER_PORT))
            p.start()
        except Exception as e:
            print(e)
