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
from typing import Literal, Tuple, List, Dict
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
    def __init__(self):
        with open("json/setting.json") as setting_file:
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

# class for waveform
# testing class
class WaveSetting:
    def __init__(self) -> None:
        with open("setting_json/wave_setting.json") as setting_file:
            params=json.load(setting_file)
            self.samplerate: int = params["samplerate"]
            self.time_prefix : str = params["time_prefix"]
            self.voltage_prefix: str = params["voltage_prefix"]
            self.timespan : list[int] = params["timespan"]

class RecordSetting:
    def __init__(self) -> None:
        with open("setting/record_setting.json") as setting_file:
            params=json.load(setting_file)
            self.spkc_samplerate: int = params["spkc_samplerate"]
            self.event_ch : str = params["event_ch"]
            self.lfp_ts_ch: str = params["lfp_ts_ch"]
            
