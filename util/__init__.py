import pandas as pd
import math
import numpy as np
import threading
import multiprocessing
import os

def isnan(value):
    is_nan_np_status = False
    is_nan_pd_status = False
    is_nan_mt_status = False
    is_nan_c1_status = False
    is_nan_c2_status = False
    try:
        is_nan_mt_status =  math.isnan(value)
    except:
        pass
    try:
        is_nan_np_status = np.isnan(value)
    except:
        pass
    try:
        is_nan_pd_status = pd.isna(value)
    except:
        pass
    try:
        if value != value:
            is_nan_c1_status = True
    except:
        pass
    try:
        if str(value) == "nan":
            is_nan_c2_status = True
    except:
        pass

    return any([is_nan_np_status, is_nan_pd_status, is_nan_mt_status, is_nan_c1_status, is_nan_c2_status])



def getThreadByName(name):
    threads = threading.enumerate() #Threads list
    for thread in threads:
        if thread.name == name:
            return thread

def getProcessByName(name):
    processes = multiprocessing.active_children() #Processes list
    for process in processes:
        if process.name == name:
            return process

def terminate_process_by_id(pid):
    try:
        stop_server_command = f"taskkill /PID {pid} /F /T"
        os.system(f'{stop_server_command}')
    except Exception as e:
        print(e)
