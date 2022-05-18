"""
作成した各種ライブラリを2022年4月時に坂上が使用している形で処理描画を行う部分
とりあえず困ったらここの関数使いましょう。
"""
from collections import defaultdict
import datetime as dt

# import original methods
from NeuroProcessing.Filter import *
from NeuroProcessing.MatProcessing import *
from NeuroProcessing.OscilloProcessing import bin_to_samplerate_and_arrays
from NeuroProcessing.Plot import plot_abr, plot_lfp, plot_csd, plot_fourier_spectal_from_dic, plot_wave, plot_fft
from NeuroProcessing.Setting import *
from NeuroProcessing.TDTProcessing import *
from NeuroProcessing.WaveStats import *

def get_abr_data_from_mat_file_dir(dir_path: Path,setting_instance: PlotSetting):
    # 各波形から最大の振幅を取り出し、それを統計量として各加算回数による低下を描画
    # ファイルの取り出し
    plx_filelist= list(dir_path.glob("*.mat"))
    #各ファイルに対してLFPの描画・CSDの描画・ABRの描画を行う
    abr_dic={}
    dir_name=plx_filelist[0].parent
    #赤コネクタ
    #channelmap=[8,9,7,10,4,13,5,12,2,15,1,16,3,14,6,11]
    #白コネクタ
    channelmap=[9,8,10,7,13,4,12,5,15,2,16,1,14,3,11,6]
    lfp_ylim=[-300,300]
    abr_ylim=[-0.3,0.3]
    csd_vrange=50
    is_diff=False
    fourier_xlim=[200,4000]
    wave_setting=WaveSetting()
    for plx_filepath in plx_filelist:
        print(plx_filepath.name)
        lfp_data=process_lfp_from_FP_ch(plx_filepath,-50,350,wave_setting)
        if "click" in plx_filepath.name:
            dB=re.search("click_(\d+)",plx_filepath.name).group(1)
            # info=re.search("click_(\d+)_(.*).mat",plx_filepath.name).group(2)
            # print(dB,info)
            # param=f"click_{dB}dB_{info}"
            # abr_dic[info]=process_abr(plx_filepath,[0,20],is_diff)
            param=f"click_{dB}dB"
            abr_dic[f"{dB}dB"]=process_abr(plx_filepath,[0,20],is_diff)
        elif "us_burst" in plx_filepath.name:
            try:
                vol = re.search("us_burst_(.*)_window_(.*).mat",plx_filepath.name).group(1)
                window = re.search("us_burst_(.*)_window_(.*).mat",plx_filepath.name).group(2)
                param = f"us_burst_{vol}_window_{window}%"
                abr_dic[f"{vol}_window{window}"]=process_abr(plx_filepath,[0,20],is_diff)
                # abr_dic[f"{vol}_window{window}"]=notchpass(abr_dic[f"{vol}_window{window}"],[1400,1600],40000)
                # abr_dic[f"{vol}_window{window}"]=notchpass(abr_dic[f"{vol}_window{window}"],[2900,3100],40000)
            except:
                abr_dic["sham"]=process_abr(plx_filepath,[0,20],is_diff)
                param="sham"
        elif "us_cont" in plx_filepath.name:
            vol = re.search("us_cont_(.*)_window_(.*).mat",plx_filepath.name).group(1)
            window = re.search("us_cont_(.*)_window_(.*).mat",plx_filepath.name).group(2)
            param = f"us_cont_{vol}_window_{window}"
            abr_dic[f"{vol}\nwindow{window}"]=process_abr(plx_filepath,[0,20],is_diff)
        plot_lfp(lfp_data,channelmap,lfp_ylim,param)
        plot_csd(lfp_data,channelmap,[-50,350],csd_vrange,param)
    plot_fourier_spectal_from_dic(abr_dic,dir_name,fourier_xlim,40000)
    if "click" in plx_filelist[-1].name:
        title= "ABR_from_EDIF_click"
    elif "us_burst" in plx_filelist[-1].name:
        title= "ABR_from_EDIF_us_burst"
        #abr_dic=notch_filtered_dict(abr_dic,[1400,1600],40000)
        #abr_dic=notch_filtered_dict(abr_dic,[2900,3100],40000)
    elif "us_cont" in plx_filelist[-1].name:
        title= "ABR_from_EDIF_us_cont"
    plot_abr(abr_dic,title,dir_name.name,abr_ylim)

def plot_oscillo_data(samplerate,time,vol_wave,title,dir_name,offset_in_ms):
    print(f"loading {dir_name} data")
    fig=plt.figure(figsize=(18,12),dpi=50,tight_layout=True)
    #波形データをrow=0にfftデータをrow=1に保存する
    axes = fig.subplots(2, 3)
    time+=offset_in_ms
    wide_xlim=[-10,110]
    narrow_xlim=[0,2]
    cent_freq_xlim=[0,0.01]
    us_cent_freq_in_KHz=int(re.search("freq_(\d+)",dir_name).group(1))
    freq_us_range=[(us_cent_freq_in_KHz*1000-50000),(us_cent_freq_in_KHz*1000+50000)]
    if not(os.path.exists(f"./waveplot")):
        os.mkdir(f"./waveplot")
    if not(os.path.exists(f"./waveplot/{dir_name}")):
        os.mkdir(f"./waveplot/{dir_name}")
    plot_wave(axes,[0,0],time,vol_wave,wide_xlim,"whole voltage")
    plot_wave(axes,[0,1],time,vol_wave,narrow_xlim,f"{narrow_xlim[0]}ms-{narrow_xlim[1]}ms")
    plot_wave(axes,[0,2],time,vol_wave,cent_freq_xlim,f"{cent_freq_xlim[0]}ms-{cent_freq_xlim[1]}ms")
    plot_fft(axes,[1,0],vol_wave,samplerate,[0,1200000],f"0-1200000Hz")
    plot_fft(axes,[1,1],vol_wave,samplerate,[1000,7000], f"1000-7000Hz")
    plot_fft(axes,[1,2],vol_wave,samplerate,freq_us_range, f"{freq_us_range[0]}-{freq_us_range[1]}Hz")
    plt.savefig(f"./waveplot/{dir_name}/{title}.png")
    plt.cla()
    plt.clf()
    plt.close(fig)
    del axes,time,vol_wave,fig
    gc.collect()
    return 
    
def append_statistic_data(voltage_wave,samplerate,is_averaged,df,name,single_dir,bin_file):
    freq,Amp=acquire_amp_spectrum(voltage_wave,samplerate)
    freq_audible_range=[200,800000]
    audible_range_ave_spectrum=acquire_average_spectrum(freq,Amp,freq_audible_range)
    audible_range_max_spectrum_value,audible_range_max_spectrum_freq = acquire_max_spectrum_value_and_freq(freq,Amp,freq_audible_range)
    us_cent_freq_in_KHz=int(re.search("freq_(\d+)",single_dir.name).group(1))
    freq_us_range=[(us_cent_freq_in_KHz*1000-50000),(us_cent_freq_in_KHz*1000+50000)]
    us_range_ave_spectrum=acquire_average_spectrum(freq,Amp,freq_us_range)
    us_range_max_spectrum_value,us_range_max_spectrum_freq = acquire_max_spectrum_value_and_freq(freq,Amp,freq_us_range)
    #可聴域周波数帯を抽出
    freq_audible_low_range=[200,3000]
    freq_audible_middle_range=[3000,60000]
    freq_audible_high_range=[60000,80000]
    audible_low_range_sum=acquire_sum_spectrum(freq,Amp,freq_audible_low_range)
    audible_middle_range_sum=acquire_sum_spectrum(freq,Amp,freq_audible_middle_range)
    audible_high_range_sum=acquire_sum_spectrum(freq,Amp,freq_audible_high_range)
    dist_in_mm=int(re.search("dist_(\d+)mm",single_dir.name).group(1))
    window_percentage=float(re.search("window_(\d+)",bin_file.name).group(1))
    window_percentage=round(window_percentage,3)
    if window_percentage <= 0.1:
        window_type="rectangle"
    else:
        window_type="humming"
        
    if "us_burst" in single_dir.name:
        stim_type="us_burst"
    elif "us_cont" in single_dir.name:
        stim_type="us_cont"
    else:
        stim_type="undefined"
    max_voltage=np.max(voltage_wave)
    side_band_peak_value,side_band_freq=acquire_side_band_value_and_freq(freq,Amp,freq_us_range)
    #計測したデータをpdに書き込み
    stim_name=bin_file.stem[:-2]
    if is_averaged:
        trial="average"
    else:
        trial=bin_file.stem[-1]
    data=[stim_name,trial,us_cent_freq_in_KHz,dist_in_mm,stim_type,
        window_percentage,max_voltage,window_type,audible_range_ave_spectrum,
        audible_range_max_spectrum_value,audible_range_max_spectrum_freq,
        us_range_ave_spectrum,us_range_max_spectrum_value,us_range_max_spectrum_freq,
        audible_low_range_sum,audible_middle_range_sum,audible_high_range_sum,
        side_band_peak_value,side_band_freq
        ]
    record = pd.Series(data, index=df.columns,name=name)
    df.append(record)
    return

def plot_and_make_df(data_dirs):
    #データを保存するようのデータフレームの作成
    cols=["stim_name","trial","cent_freq","distance","type","window_percentage","max_voltage",
        "window_type","audible_range_spectrum_ave","audible_range_max_spectrum_value","audible_range_max_spectrum_freq",
        "us_range_ave_spectrum","us_range_max_spectrum_value","us_range_max_spectrum_freq",
        "audible_low_range_sum","audible_middle_range_sum","audible_high_range_sum",
        "side_band_peak_value","side_band_peak_freq"]
    statistic_df=pd.DataFrame(index=[],columns=cols)
    cnt=0
    for single_dir in data_dirs:
        bin_files=list(single_dir.glob("*"))
        for ind,bin_file in enumerate(bin_files):
            print(f"processing {bin_file.name}")
            samplerate,time_data,voltage_wave=bin_to_samplerate_and_arrays(bin_file)
            title=bin_file.name[:-4]
            plot_oscillo_data(samplerate,time_data,voltage_wave,title,single_dir.name,40)
            append_statistic_data(voltage_wave,samplerate,is_averaged=False,df=statistic_df,name=cnt,single_dir=single_dir,bin_file=bin_file)
            cnt+=1
            print(f"record is appended: {cnt}")
            if ind == 0:
                wave_data=np.array([])
            elif ind == len(bin_files)-1 or bin_files[ind].name[:-6] != bin_files[ind-1].name[:-6]:
                averaged_wave=np.mean(wave_data,axis=0)
                title=bin_file.name[:-5]+"ave"
                plot_oscillo_data(samplerate,time_data,averaged_wave,title,single_dir.name,40)
                append_statistic_data(averaged_wave,samplerate,is_averaged=True,df=statistic_df,name=cnt,single_dir=single_dir,bin_file=bin_file)
                cnt+=1
                print(f"record is appended: {cnt}")
                wave_data=np.array([])
            elif bin_files[ind].name[:-6] == bin_files[ind-1].name[:-6]:
                if len(wave_data)==0:
                    wave_data=voltage_wave
                else:
                    wave_data=np.vstack(wave_data,voltage_wave)
    today = dt.datetime.now()
    date_info=today.strftime("%y%m%d_%H%M")
    statistic_df.to_excel(f"statistic_data_{date_info}.xlsx",index=False)