#modules
import pandas as pd
import numpy as np
import json
import os, sys
import scipy.io
from scipy import signal
import matplotlib.pyplot as plt
import statistics
import math
import gc
import warnings
from pathlib import Path
import re
import json
from typing import Literal, Tuple, List, Dict, Union
import struct
from decimal import *
import csv
from tokenize import String



#numpyをjsonで出力できるように修正
class NumpyEncoder(json.JSONEncoder):
    """how to use
    numpy_structure=(** array or dict etc ... with numpy structure**)
    json.dumps(numpy_structrue , cls=NumpyEncoder)
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)


class PlotSetting():
    def __init__(self,json_filename:str = ""):
        if len(json_filename)==0:
                json_filename="setting_json/plot_setting.json"
        with open(json_filename) as setting_file:
            params=json.load(setting_file)
            self.xlim: list[float] = params["xlim"]
            self.ylim: list[float] = params["ylim"]
            self.channelmap: list[int] =params["channelmap"]
            self.samplerate: int = params["samplerate"]
            self.linewidth: float = params["linewidth"]
            self.xlabel: str= params["xlabel"]
            self.ylabel: str = params["ylabel"]
            self.title : str = params["title"]
            self.lfp_ylim: list[float] = params["lfp_ylim"]
            self.abr_ylim: list[float] = params["abr_ylim"]
            self.csd_vrange: int = params["csd_vrange"]

class WaveSetting:
# class for waveform
# testing class
    def __init__(self,json_filename:str = ""):
        if len(json_filename)==0:
            json_filename="setting_json/wave_setting.json"
        with open(json_filename) as setting_file:
            params=json.load(setting_file)
            self.samplerate: int = params["samplerate"]
            self.time_prefix : str = params["time_prefix"]
            self.voltage_prefix: str = params["voltage_prefix"]
            self.timespan : list[int] = params["timespan"]

class RecordSetting:
    def __init__(self,json_filename:str = ""):
        if len(json_filename)==0:
            json_filename="setting_json/record_setting.json"
        with open(json_filename) as setting_file:
            params=json.load(setting_file)
            self.spkc_samplerate: int = params["spkc_samplerate"]
            self.event_ch : str = params["event_ch"]
            self.lfp_ts_ch: str = params["lfp_ts_ch"]
            
def get_args(func:function):
    arg_names = func.__code__.co_varnames
    return arg_names

def extract_valid_args(kwargs_dict:dict, arg_names_or_func:Union[function,list,set]):
    if arg_names_or_func is function:
        arg_names=get_args(arg_names_or_func)
    else:
        arg_names=arg_names_or_func
    res_dict={}
    not_used_args=[]
    for key,value in kwargs_dict.items():
        if key in arg_names:
            res_dict[key]=value
        else:
            not_used_args.appned(key)
    print("these args aren't used in this function")
    print(*not_used_args)
    return res_dict