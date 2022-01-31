import pandas as pd
import math
import numpy as np

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