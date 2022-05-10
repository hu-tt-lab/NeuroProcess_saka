import numpy as np


def acquire_peak_uv_and_latency_ms(waveform,time_range_ms,samplerate,detect_span_ms):
    """acquire peak and latency of single waveform

    Args:
        waveform (list or numpy.ndarray)): _description_
        time_range (list[float]): _description_
        samplerate (int): _description_
        detect_span (list[float]): _descritption_ 
    """
    samplerate_ms=samplerate//1000
    timepoints=np.arange(time_range_ms[0],time_range_ms[1],1/samplerate_ms)
    # 検出区間の中から最大値(最小値)を検出
    wave_detect_span=waveform[timepoints[timepoints==detect_span_ms[0]][0]:timepoints[timepoints==detect_span_ms[1]][0]]
    if type(waveform)==list:
        wave_detect_span=np.array(wave_detect_span)
    peak_voltage_uv=np.max(np.abs(wave_detect_span))
    peak_latency_ms=np.argmax(np.abs(wave_detect_span))*samplerate
    peak_latency_ms=peak_latency_ms+detect_span_ms[0]
    
    return peak_voltage_uv,peak_latency_ms

def acquire_zscore_at_one_point(waveform,samplerate,time_range_ms,base_span_ms,timepoint_ms):
    samplerate_ms=samplerate//1000
    timepoints=np.arange(time_range_ms[0],time_range_ms[1],1/samplerate_ms)
    base_span=waveform[timepoints[timepoints==base_span_ms[0]]:timepoints[timepoints==base_span_ms[1][0]]]
    if type(waveform)==list:
        base_span=np.array(base_span)
    voltage=waveform[timepoints[timepoints==timepoint_ms][0]]
    base_mean=np.mean(base_span)
    base_std=np.std(base_span)
    zscore=(voltage-base_mean)/base_std
    
    return zscore