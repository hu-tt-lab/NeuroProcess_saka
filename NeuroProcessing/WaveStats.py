import gc
import numpy as np
from scipy.signal import find_peaks

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

def acquire_max_spectrum_value_and_freq(freq:np.ndarray ,amp:np.ndarray, target_freq_range:list[float]):
    left_point=np.where(freq==freq[freq>=target_freq_range[0]][0])[0][0]
    right_point=np.argmax(freq[freq<=target_freq_range[1]])
    max_amp=np.max(amp[left_point:right_point])
    max_amp_ind=np.argmax(amp[left_point:right_point])
    target_freq_range=freq[left_point:right_point]
    target_freq=target_freq_range[max_amp_ind]
    del target_freq_range
    gc.collect()
    return max_amp,target_freq

def acquire_sum_spectrum(freq:np.ndarray, amp:np.ndarray, target_freq_range:list[float]):
    left_point=np.where(freq==freq[freq>=target_freq_range[0]][0])[0][0]
    right_point=np.argmax(freq[freq<=target_freq_range[1]])
    sum_spectrum=np.sum(amp[left_point:right_point])
    return sum_spectrum

def acquire_average_spectrum(freq:np.ndarray,amp:np.ndarray,target_freq_range:list[float]):
    left_point=np.where(freq==freq[freq>=target_freq_range[0]][0])[0][0]
    right_point=np.argmax(freq[freq<=target_freq_range[1]])
    mean_spectrum=np.mean(amp[left_point:right_point])
    return mean_spectrum

def find_peaks_from_spectrum(freq:np.ndarray, amp:np.ndarray, target_freq_range:list[float], width:int):
    left_point=np.where(freq==freq[freq>=target_freq_range[0]][0])[0][0]
    right_point=np.argmax(freq[freq<=target_freq_range[1]])
    peaks_ind,_=find_peaks(amp[left_point:right_point],width=width)
    return peaks_ind

def acquire_indexes_from_fftfreq(freq:np.ndarray,target_freq_range:list[float]):
    left_point=np.where(freq==freq[freq>=target_freq_range[0]][0])[0][0]
    right_point=np.argmax(freq[freq<=target_freq_range[1]])
    return left_point,right_point

def acquire_side_band_value_and_freq(freq,Amp,target_freq_range):
    peaks_ind=find_peaks_from_spectrum(freq,Amp,target_freq_range,3)
    left_point=np.where(freq==freq[freq>=target_freq_range[0]][0])[0][0]
    right_point=np.argmax(freq[freq<=target_freq_range[1]])
    peak_freqs=freq[left_point:right_point][peaks_ind]
    peak_Amps=Amp[left_point:right_point][peaks_ind]
    Amps_arg_sorted=np.argsort(peak_Amps)
    side_band_peaks=peak_Amps[Amps_arg_sorted[-2]]
    side_band_cent_freq=peak_freqs[Amps_arg_sorted[-2]]
    return side_band_peaks,side_band_cent_freq

if __name__ == "__main__":
    datas=np.linspace(-50,350,400*40)
    v,i=acquire_peak_uv_and_latency_ms(datas,[-50,350],40000,[0,100])
    print(v,i)
    print(datas[int((50+99.975)*40)])
