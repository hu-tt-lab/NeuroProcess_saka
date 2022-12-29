import itertools
import matplotlib.pyplot as plt
import numpy as np
import os 
import scipy 
import pandas as pd
from NeuroProcessing.Setting import MakingIdealUSWaveform

def making_cont_stim_waveform(cont_duration_ms, cont_window ,MakingWaveformInfo:MakingIdealUSWaveform):
    samplerate_ms = MakingWaveformInfo.samplerate_ms
    duration_ms = MakingWaveformInfo.duration_ms
    offset_span_ms = MakingWaveformInfo.offset_span_ms
    offset_ms = MakingWaveformInfo.offset_ms
    centfreq = MakingWaveformInfo.centfreq
    after_onset_span = np.zeros(samplerate_ms*duration_ms)
    stim_timespan_ms = np.arange(0,cont_duration_ms,1/samplerate_ms)
    stim_wave = np.sin(centfreq//1000*2*np.pi*stim_timespan_ms)
    #各時間帯に窓をかける
    if cont_window>0:
        window = cont_window/2
        window_samples = int(len(stim_wave)*window/100)
        upper_window = np.sin(np.pi/window_samples/2*np.arange(0,window_samples))
        lower_window = np.sin(np.pi-(np.pi/window_samples/2*np.arange(window_samples-1,-1,-1)))
        stim_wave[:window_samples]*=upper_window
        stim_wave[-window_samples:]*=lower_window
    after_onset_span[:len(stim_timespan_ms)] = stim_wave
    stim_wave = np.concatenate([offset_span_ms,after_onset_span])
    time_span = np.linspace(offset_ms,duration_ms,len(stim_wave))
    return stim_wave,time_span

def making_burst_stim_waveform(burst_stim_duration,burst_pulse_duration,prf,burst_window, MakingWaveformInfo:MakingIdealUSWaveform):
    samplerate_ms = MakingWaveformInfo.samplerate_ms
    # 波形生成部分
    offset_span_ms = MakingWaveformInfo.offset_span_ms
    after_onset_span = np.zeros(int(samplerate_ms*MakingWaveformInfo.duration_ms))
    # pulse_durationをもとに単パルスの形を生成
    single_pulse_time_ms = 1/prf*1000
    single_pulse_span = np.arange(0,single_pulse_time_ms,1/samplerate_ms)
    single_wavespan_ms = np.arange(0,burst_pulse_duration,1/samplerate_ms)
    single_pulse_wave = np.sin(MakingWaveformInfo.centfreq//1000*2*np.pi*single_wavespan_ms)
    pulse_num = burst_stim_duration//single_pulse_time_ms
    if burst_window > 0:
        # 各パルスの形を生成
        window = burst_window/2
        window_samples = int(len(single_pulse_wave)*window/100)
        upper_window = np.sin(np.pi/window_samples/2*np.arange(0,window_samples))
        lower_window = np.sin(np.pi-(np.pi/window_samples/2*np.arange(window_samples-1,-1,-1)))
        single_pulse_wave[:window_samples]*=upper_window
        single_pulse_wave[(-window_samples):]*=lower_window
        single_pulse_wave[-1] = 0
    single_pulse_with_offset = np.zeros_like(single_pulse_span)
    single_pulse_with_offset[:len(single_pulse_wave)] = single_pulse_wave
    #パルス数分波形を重ね合わせ
    after_onset_stim_span = np.concatenate([single_pulse_with_offset for _ in range(int(pulse_num))])
    if len(after_onset_stim_span)>len(after_onset_span):
        after_onset_stim_span = np.concatenate([single_pulse_with_offset for _ in range(int(pulse_num)-1)])
    after_onset_span[:len(after_onset_stim_span)] = after_onset_stim_span
    stim_wave = np.concatenate([offset_span_ms,after_onset_span])
    time_span = np.linspace(MakingWaveformInfo.offset_ms,MakingWaveformInfo.duration_ms,len(stim_wave))
    return stim_wave,time_span