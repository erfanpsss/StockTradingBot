from pyexpat import model
from django.db import models
import threading
import multiprocessing
from util import getThreadByName, getProcessByName
from django.conf import settings
import os
from .seperate_process_funcs import run_command_from_process

class RunnerStatus(models.Model):
    id = models.AutoField(primary_key=True)
    enable = models.BooleanField(default=False)
    enable_finviz = models.BooleanField(default=False)
    enable_strategies = models.BooleanField(default=False)
    loop_wait = models.IntegerField(default=60)
    last_run_time = models.DateTimeField(blank = True, null = True)

    def __str__(self):
        return "Active" if self.enable else "Inactive"

    class Meta:
        verbose_name = "Runner"
        verbose_name_plural = "Runner"

    def stop(self):
        self.enable = False
        self.save()

    def handle_start_runner(self):
        from runner.runner import Runner
        
        if self.enable:
            try:
                existing_thread = getProcessByName("Runner")
                existing_thread.join()
            except:
                pass

            command = (
                f"cd {str(settings.BASE_DIR)} &"
                f"{settings.PYTHON_EXE} manage.py start_runner"
            )
            
            process = multiprocessing.Process(target=run_command_from_process, name='Runner', args=(command,))
            process.start()

        elif not self.enable:
            try:
                existing_thread = getProcessByName("Runner")
                existing_thread.join()
            except:
                pass

    def save(self, *args, **kwargs):
        if not self.pk and RunnerStatus.objects.count() >= 1:
            return
        super().save(*args, **kwargs)
        self.handle_start_runner()

