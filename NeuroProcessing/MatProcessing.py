import numpy as np
import scipy.io
from scipy import signal

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


def process_lfp_from_FP_ch(plx_filepath,offset,onset,setting_instance):
        #取得したpathを元にLFP波形を取得・加算平均を行う
    mat_data=scipy.io.loadmat(plx_filepath)
    #timestampの取得
    spkc_samplerate=setting_instance.spkc_samplerate
    event_ch_name=setting_instance.event_ch
    if event_ch_name in mat_data:
        trigger_wave = mat_data[event_ch_name]
        trigger_wave = list(trigger_wave[j][0] for j in range(len(trigger_wave)))
        #sオーダーで刺激印加時間があるためindex表記に直す
        timestamp_fp = list(round(trigger_wave[i]-float(mat_data["FP01_ts"][0]),3)*1000 for i in range(len(trigger_wave)))
        timestamp_fp = list(map(int,timestamp_fp))
    else:
        trigger_wave= mat_data[setting_instance.low_trigger_ch]
        trigger_wave = list(trigger_wave[j][0] for j in range(len(trigger_wave)))
        spkc_timestamp=get_timestamp_from_law_ch(trigger_wave,0.05,0.3,spkc_samplerate)
        timestamp_time=(np.array(spkc_timestamp)+(mat_data["FP01_ts"][0]-mat_data["SPKC20_ts"][0])*spkc_samplerate)/(spkc_samplerate//1000)
        timestamp_fp=list(map(round,timestamp_time))
    datas=[]
    for i in range(1, 17):
        fp_name = f"FP{str(i).zfill(2)}"
        each_channel_wave = mat_data[fp_name]
        each_channel_wave = list(
            each_channel_wave[j][0] for j in range(len(each_channel_wave)))
        index = 0
        each_ch_wave=np.zeros(onset+offset)
        for timepoint in timestamp_fp:
            each_wave = np.array(
                each_channel_wave[timepoint-offset:timepoint+onset])
            each_ch_wave+=each_wave
            index+=1
        #加算回数で割ってμVに直す
        each_ch_wave/=index
        each_ch_wave*=1000
        datas.append(each_ch_wave)
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
        