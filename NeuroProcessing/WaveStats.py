import wave
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
    if isinstance(waveform,list):
        waveform=np.array(waveform)
    wave_detect_span=waveform[int((detect_span_ms[0]-time_range_ms[0])*samplerate_ms):int((detect_span_ms[1]-time_range_ms[0])*samplerate_ms)]
    if type(waveform)==list:
        wave_detect_span=np.array(wave_detect_span)
    peak_voltage_uv=np.max(np.abs(wave_detect_span))
    peak_latency_ms=np.argmax(np.abs(wave_detect_span))/samplerate_ms
    peak_latency_ms=peak_latency_ms+detect_span_ms[0]
    
    return peak_voltage_uv,peak_latency_ms

def acquire_zscore_at_one_point(waveform,samplerate,time_range_ms,base_span_ms,timepoint_ms):
    samplerate_ms=samplerate//1000
    timepoints=np.arange(time_range_ms[0],time_range_ms[1],1/samplerate_ms)
    if isinstance(waveform,list):
        waveform=np.array(waveform)
    base_span=waveform[int((base_span_ms[0]-time_range_ms[0])*samplerate_ms):int((base_span_ms[1]-time_range_ms[0])*samplerate_ms)]
    if type(waveform)==list:
        base_span=np.array(base_span)
    voltage=waveform[int((timepoint_ms-time_range_ms[0])*samplerate_ms)]
    base_mean=np.mean(base_span)
    base_std=np.std(base_span)
    zscore=(voltage-base_mean)/base_std
    
    return zscore

def acquire_wave_stats_data_from_list_or_dict(data_list_or_dict,total_span_ms,noise_span_ms,signal_span_ms,samplerate):
    result_dict={}
    if type(data_list_or_dict)==list:
        index=range(1,len(data_list_or_dict)+1)
        data_list_or_dict=dict(zip(index,data_list_or_dict))
    for key,waveform in data_list_or_dict.items():
        peak_voltage_uv,peak_latency_ms=acquire_peak_uv_and_latency_ms(waveform,total_span_ms,samplerate,signal_span_ms)
        zscore=acquire_zscore_at_one_point(waveform,samplerate,total_span_ms,noise_span_ms,peak_latency_ms)
        result_dict[key]={"peak_voltage[uV]":peak_voltage_uv, "peak_latency[ms]": peak_latency_ms,"zscore":zscore}
    return result_dict

if __name__ == "__main__":
    datas=np.linspace(-50,350,400*40)
    v,i=acquire_peak_uv_and_latency_ms(datas,[-50,350],40000,[0,100])
    print(v,i)
    print(datas[int((50+99.975)*40)])
