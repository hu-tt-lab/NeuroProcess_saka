from sqlite3 import Timestamp
import wave
import numpy as np
import pandas as pd
import scipy.io
from scipy import signal
from typing import List, Union
#import own function
from NeuroProcessing.Filter import lowpass
from NeuroProcessing.Setting import PlotSetting, RecordSetting, WaveSetting

def diff_by_block(base,compare,block_size):
    # 長い配列を部分ごとに区切って足す
    # メモリ的な余裕ができる
    if len(base)!=len(compare):
        print("base and compare must be same langth")
        return 
    ans = np.zeros(len(base))
    i = 0
    while i*block_size<len(base):
        if (i+1)*block_size < len(base):
            partial=base[i*block_size:(i+1)*block_size]-compare[i*block_size:(i+1)*block_size]
            ans[i*block_size:(i+1)*block_size]+=partial
        else:
            partial=base[i*block_size:len(base)]-compare[i*block_size:(i+1)*len(compare)]
            ans[i*block_size:len(base)]+=partial
        i+=1
    return ans

def get_timestamp_from_law_ch(single_channel_data,Th,isi,samplerate):
    timestamp=[]
    i=0
    while i<len(single_channel_data):
        if single_channel_data[i]>=Th:
            timestamp.append(i)
            i+=int(isi*samplerate)
        i+=1
    return timestamp


def acquire_lfp_timestamps_from_mat_data(mat_data, record_setting:RecordSetting):
    #timestampの取得
    spkc_samplerate=record_setting.spkc_samplerate
    event_ch_name=record_setting.event_ch
    print(mat_data.keys())
    print(event_ch_name in mat_data)
    if event_ch_name in mat_data:
        trigger_wave = mat_data[event_ch_name]
        trigger_wave = list(trigger_wave[j][0] for j in range(len(trigger_wave)))
        #sオーダーで刺激印加時間があるためindex表記に直す
        timestamp_fp = list(round(trigger_wave[i]-float(mat_data["FP01_ts"][0]),3)*1000 for i in range(len(trigger_wave)))
        timestamp_fp = list(map(int,timestamp_fp))
    else:
        trigger_wave= mat_data[record_setting.law_trigger_ch]
        trigger_wave = list(trigger_wave[j][0] for j in range(len(trigger_wave)))
        spkc_timestamp=get_timestamp_from_law_ch(trigger_wave,0.05,0.3,spkc_samplerate)
        timestamp_time=(np.array(spkc_timestamp)+(mat_data["FP01_ts"][0]-mat_data["SPKC20_ts"][0])*spkc_samplerate)/(spkc_samplerate//1000)
        timestamp_fp=list(map(round,timestamp_time))
    return timestamp_fp

def additional_average_based_timestamps(mat_data,timestamp_fp: List[int] ,onset_ms:int, offset_ms: int, record_setting: RecordSetting):
    datas=[]
    for i in range(1, 17):
        fp_name = f"FP{str(i).zfill(2)}"
        each_channel_wave = mat_data[fp_name]
        each_channel_wave = list(
            each_channel_wave[j][0] for j in range(len(each_channel_wave)))
        index = 0
        each_ch_wave=np.zeros(np.abs(onset_ms-offset_ms))
        for timepoint in timestamp_fp:
            each_wave = np.array(
                each_channel_wave[timepoint+offset_ms:timepoint+onset_ms])
            if len(each_ch_wave)==len(each_wave):
                each_ch_wave+=each_wave
                index+=1
        #加算回数で割ってμVに直す
        each_ch_wave/=index
        each_ch_wave*=1000
        datas.append(each_ch_wave)
    return datas

def process_lfp_from_FP_ch_based_abr_order(plx_filepath,abr_order_path, offset_ms, onset_ms, record_setting:RecordSetting):
    """刺激名で取り出すのが面倒なのでdatasをlistに格納する形でreturnする

    Args:
        plx_filepath (_type_): _description_
        abr_order (_type_): _description_
        offset_ms (_type_): _description_
        onset_ms (_type_): _description_
        record_setting (RecordSetting): _description_
    Return:
        all_lfp_datas (List[List]): collection of each lfp response matrix(shape is [16][data length])
    """
    mat_data=scipy.io.loadmat(plx_filepath)
    timestamp_fp= acquire_lfp_timestamps_from_mat_data(mat_data, record_setting)
    #abr_order_fileの読み込み
    abr_order=pd.read_csv(abr_order_path)
    #刺激の回数だけがほしいので取り出し
    ind=0
    all_lfp_datas=[]
    for trial in abr_order["trial"]:
        each_stim_timestamps=timestamp_fp[ind:ind+trial]
        datas=additional_average_based_timestamps(mat_data,each_stim_timestamps,onset_ms, offset_ms, record_setting)
        ind+=trial
        all_lfp_datas.append(datas)
    return all_lfp_datas
    
    

def process_lfp_from_FP_ch(plx_filepath,offset_ms,onset_ms,record_setting:RecordSetting):
    """processed single stimulation to lfp

    Args:
        plx_filepath (_type_): _description_
        offset_ms (_type_): _description_
        onset_ms (_type_): _description_
        record_setting (RecordSetting): _description_

    Returns:
        list: lfp_voltage_datas_array
    """
    #取得したpathを元にLFP波形を取得・加算平均を行う
    mat_data=scipy.io.loadmat(plx_filepath)
    #timestampの取得
    timestamp_fp = acquire_lfp_timestamps_from_mat_data(mat_data,record_setting)
    #timestampに基づいた加算平均の処理
    datas= additional_average_based_timestamps(mat_data,timestamp_fp,onset_ms, offset_ms, record_setting)
    return datas



def process_abr(plx_filepath,xlim,is_diff):
    mat_data=scipy.io.loadmat(plx_filepath)
    samplerate=40000
    event_ch_name="EVT01"
    if event_ch_name in mat_data:
        trigger_wave = mat_data["EVT01"]
        trigger_wave = list(trigger_wave[j][0] for j in range(len(trigger_wave)))
        #sオーダーで刺激印加時間があるためindex表記に直す
        timestamp = list(round(trigger_wave[i]-mat_data["SPKC17_ts"][0][0],6)*samplerate for i in range(len(trigger_wave)))
        timestamp = list(map(int,timestamp))
    else:
        trigger_wave= mat_data[f"SPKC{str(32).zfill(2)}"]
        trigger_wave = list(trigger_wave[j][0] for j in range(len(trigger_wave)))
        timestamp=get_timestamp_from_law_ch(trigger_wave,0.05,0.08,samplerate)
    if is_diff:
        active_name="SPKC18"
        reference_name="SPKC19"
        active_channel_wave=mat_data[active_name]
        active_channel_wave=np.array(list(active_channel_wave[j][0] for j in range(len(active_channel_wave))))
        reference_channel_wave=mat_data[reference_name]
        reference_channel_wave=np.array(list(reference_channel_wave[j][0] for j in range(len(reference_channel_wave))))
        each_channel_wave=diff_by_block(active_channel_wave,reference_channel_wave,10000)
    else:
        spkc_name = f"SPKC17"
        each_channel_wave = mat_data[spkc_name]
        each_channel_wave = list(
            each_channel_wave[j][0] for j in range(len(each_channel_wave)))
    filter_range=[3000,4000]
    each_channel_wave=lowpass(each_channel_wave,samplerate,filter_range[0],filter_range[1],3,30)
    offset=xlim[0]
    onset=xlim[1]
    total_wave=np.zeros(abs(int((onset-offset)*samplerate/1000)))
    index=0
    for timepoint in timestamp:
        each_wave=np.array(each_channel_wave[timepoint+int(offset*samplerate/1000):timepoint+int(onset*samplerate/1000)])
        total_wave+=each_wave
        index+=1
    #加算回数で割ってμVに直す
    total_wave/=index
    total_wave*=1000
    return total_wave

def substract_mean_of_base_span(waveform : Union[np.ndarray,list], base_span:list[int] = [0,50]):
    base_span_data=waveform[base_span[0],base_span[1]]
    if waveform is list:
        waveform=np.array(base_span_data)
        base_span_data=np.array(base_span_data)
    base_mean=np.mean(base_span_data)
    waveform-=base_mean    
    return waveform


def reshape_lfps(lfp_data,channelmap):
    all_waveform=[]
    for channel in channelmap:
        wave=np.array(lfp_data[channel-1]) 
        if len(all_waveform)==0:
            all_waveform=np.array([wave])
        else:
            all_waveform=np.vstack([all_waveform,wave])
    return all_waveform

def remove_dc_bias(waveform,samplerate,total_range_ms,base_range_ms):
    if len(waveform) == 16:
        result_waveform = [] 
        for each_wave in waveform:
            averaged_waveform = remove_dc_bias_one_channel(each_wave,samplerate,total_range_ms,base_range_ms)
            result_waveform.append(averaged_waveform)
    else:
        result_waveform =remove_dc_bias_one_channel(waveform,samplerate,total_range_ms,base_range_ms)
    return result_waveform
    
def remove_dc_bias_one_channel(waveform,samplerate,total_range_ms,base_range_ms):
    samplerate_ms = samplerate//1000
    indexes = np.arange(total_range_ms[0],total_range_ms[1],samplerate_ms)
    target_time_start = np.where(indexes==base_range_ms[0])[0][0]
    target_time_end = np.where(indexes==base_range_ms[1])[0][0]
    target_range = waveform[target_time_start:target_time_end]
    dc_bias  = np.mean(target_range)
    return waveform-dc_bias
    
    

#test code
if __name__ == "__main__":
    record_setting=RecordSetting()