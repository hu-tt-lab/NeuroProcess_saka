import re
from turtle import color
import numpy as np
from matplotlib import pyplot as plt
import os
import gc

# import own function
from NeuroProcessing.Setting import PlotSetting
from NeuroProcessing.MatProcessing import reshape_lfps
from NeuroProcessing.Filter import acquire_amp_spectrum, gradient_double, source,spline,acquire_power_spectrum,moving_average_for_time_direction

from NeuroProcessing.WaveStats import acquire_zscore_at_one_point

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 14

def plastic_key(key):
    vol=re.search("[0-9]+(\.[0-9]+)*V",key)
    if "sham" in key:
        return key
    if vol!=None:
        start=vol.end()+1
        vol=vol.group(0)
    else:
        print("vol not found")
        start=0
        vol=""
    params=re.findall("[a-zA-Z]+_[0-9]+\.*[0-9]*μ*[a-zA-Z]*%*",key[start:])
    params="\n".join(params)
    plasticed_key=f"{vol}_{params}"
    return plasticed_key


def plot_event(fig, axes, xlim, is_single=False):
    ax = fig.add_subplot(111, zorder=-1)
    ax.set_xlim(xlim[0], xlim[1])
    ax.spines.top.set_visible(False)
    ax.spines.right.set_visible(False)
    ax.spines.left.set_visible(False)
    ax.spines.bottom.set_position(("outward", 10))
    if not is_single:
        ax.get_shared_x_axes().join(ax, axes[0])
    ax.tick_params(left=False, labelleft=False, right=False)
    ax.set_ylim([0, 1])
    ax.plot([0, 0], [0, 1], color="k", alpha=0.3)
    return

def format_axis(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # remove ticks
    ax.tick_params(
        axis='y',          # changes apply to the y-axis
        which='both',      # both major and minor ticks are affected
        left=False,        # ticks along the left edge are off
        right=False,       # ticks along the right edge are off
        labelleft=False)   # labels along the left edge are off
    ax.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off
    return

def plot_channels(line,axes,channelmap,xlim,ylim,voltage_prefix: str="μV"):
    for ch_count,channel in enumerate(channelmap,1):
        wave=np.array(line[channel-1])
        i = ch_count-1
        # Set limits and labels
        axes[i].set_facecolor("#ffffff00")
        axes[i].set_xlim(xlim[0],xlim[1])
        axes[i].set_ylim(ylim[0],ylim[1])
        axes[i].set_ylabel(ch_count * 50, rotation=0, ha="right", va="center")
        # Plot base line
        axes[i].plot(xlim, [0, 0], color="k", alpha=0.3, linestyle="--")
        # Plot waveform
        time=range(xlim[0],xlim[1])
        axes[i].plot(time, wave, color="k", clip_on=False,)
        # Format spines and ticks
        if ch_count == len(channelmap):
            axes[i].spines['top'].set_visible(False)
            axes[i].spines['left'].set_visible(False)
            axes[i].spines['bottom'].set_visible(False)
            axes[i].spines['right'].set_position(("outward", 10))
            axes[i].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            axes[i].yaxis.tick_right()
            axes[i].set_yticks([ylim[0], 0, ylim[1]])
            axes[i].set_yticklabels([ylim[0], f"0{voltage_prefix}", ylim[1]])
        else:
            format_axis(axes[i])
    return

def get_timestamp_from_law_ch(single_channel_data,Th,isi,samplerate):
    timestamp=[]
    i=0
    while i<len(single_channel_data):
        if single_channel_data[i]>=Th:
            timestamp.append(i)
            i+=int(isi*samplerate)
        i+=1
    return timestamp

def plot_abr(abr_dic:dict,title:str,dir_name,ylim:list,left_adjust:float=0.1,is_sort:bool = True,samplerate=25000,**kwargs):
    if is_sort:
        abr_dic=dict(sorted(abr_dic.items(),reverse=True))
    if len(abr_dic)>6:
        fig_size=[10,len(abr_dic)+1]
    else:
        fig_size=[10,7]
    fig,axes= plt.subplots(nrows=len(abr_dic.keys()),sharex=True,figsize=fig_size,dpi = 600)
    fig.subplots_adjust(left=left_adjust)
    fig.patch.set_facecolor('white')
    fig.suptitle(title)
    fig.supxlabel("Time from Stimulation (ms)")
    #fig.supylabel("stim type")
    xlim=[0,20]
    
    plot_event(fig,axes,xlim)
    plot_abrs(abr_dic,axes,ylim,samplerate,**kwargs)
    if not (os.path.exists("./abr_images/")):
        os.mkdir("./abr_images")
    fig.savefig(f"./abr_images/{dir_name}_{title}.png")
    fig.clear()
    plt.close(fig)
    del axes
    del fig
    gc.collect()
    

def plot_abrs(data,axes,ylim,samplerate,p1_range:list[float]=[1.5, 2.8], base_ms:list[int]= [-10,0],xlim:list[int]=[0,20],start_time_ms:int=0,is_peak:bool = True, is_star =False,threshold = 4.36,is_plastic=True,z_score_whole_time_range = [-20, 30]):
    i=0
    keys=data.keys()
    values=data.values()
    samplerate_ms=samplerate//1000
    for key,value in zip(keys,values):
        #sampling_rate
        wave=value[int((xlim[0]-start_time_ms)*samplerate_ms):int((xlim[1]-start_time_ms)*samplerate_ms)]
        # Set limits and label
        axes[i].set_facecolor("#ffffff00")
        axes[i].set_xlim(xlim[0],xlim[1])
        axes[i].set_ylim(ylim[0],ylim[1])
        if is_plastic:
            key=plastic_key(key)
        max_timepoint=np.argmax(np.abs(value[int((p1_range[0]-start_time_ms)*samplerate_ms):int((p1_range[1]-start_time_ms)*samplerate_ms)]))/samplerate_ms+p1_range[0]
        zscore=acquire_zscore_at_one_point(value,samplerate,z_score_whole_time_range,base_ms,max_timepoint,is_abs=True)
        if zscore >= threshold and is_star:
            key="*"+key
        axes[i].set_ylabel(key, rotation=0, ha="right", va="center")
        # Plot base line
        axes[i].plot(xlim, [0, 0], color="k", alpha=0.3, linestyle="--")
        # Plot waveform
        time=np.arange(xlim[0],xlim[1],1/(samplerate/1000))
        if len(wave)<=len(time):
            time=time[:len(wave)]
        axes[i].plot(time, wave, color="k", clip_on=False,)
        if is_peak:
            max_point_y = 1
            if max_point_y < ylim[1]:
                max_point_y+=0.2
            else:
                max_point_y-=0.2
            axes[i].scatter(max_timepoint,max_point_y, color ="k", s= 50, marker ="*")
        
        # Format spines and ticks
        if i == len(keys)-1:
            axes[i].spines['top'].set_visible(False)
            axes[i].spines['left'].set_visible(False)
            axes[i].spines['bottom'].set_visible(False)
            axes[i].spines['right'].set_position(("outward", 10))
            axes[i].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            axes[i].yaxis.tick_right()
            axes[i].set_yticks([ylim[0], 0, ylim[1]])
            axes[i].set_yticklabels([str(ylim[0]), "0 μV", str(ylim[1])],fontsize=10)
        else:
            format_axis(axes[i])
        i+=1
    axes[0].scatter(0,ylim[1],marker="v",s = 300, color="k")
    axes[0].text(xlim[0]+abs(xlim[0]*0.2),ylim[1]-abs(ylim[1]*0.2),"stim onset",fontsize=14)
    return


def plot_lfp(lfp_data,channelmap,ylim,xlim,title_and_filename,save_fig_dir_name,**kwargs):
    fig, axes = plt.subplots(nrows=len(channelmap), sharex=True, figsize=[9,6])
    title=f"LFP {title_and_filename}"
    fig.patch.set_facecolor('white')
    fig.suptitle(title)
    fig.supxlabel("Time from Stimulation [ms]")
    fig.supylabel("Depth from Bran Surface [µm]")
    plot_event(fig, axes, xlim)
    plot_channels(lfp_data,axes,channelmap,xlim,ylim,**kwargs)
    if not(os.path.exists("./lfp_plot")):
        os.mkdir("./lfp_plot")
    if not(os.path.exists(f"./lfp_plot/{save_fig_dir_name}")):
        os.mkdir(f"./lfp_plot/{save_fig_dir_name}")
    fig.savefig(f'./lfp_plot/{save_fig_dir_name}/lfp_{title_and_filename}.png')
    fig.clear()
    plt.close(fig)
    del axes
    del fig
    gc.collect()
    
def plot_csd_figure(fig,ax,lfp_data,channelmap,xlim,vrange,is_gradient = False,gradient_size = 5,axis=0,inverse=False,depth_range=[0,750],ch_distance= 50,is_standardized=False,ylim=[100,700]):
    reshape_datas=reshape_lfps(lfp_data,channelmap)
    reshape_datas=np.flipud(reshape_datas)
    reshape_datas=moving_average_for_time_direction(reshape_datas,average_size=gradient_size,mode="same")
    #csd = blur(gradient_double(spline(blur(reshape_data, 3, axis=1), 4, axis=1)), 5, axis=1)
    gradient= source(reshape_datas,axis=axis,inverse=inverse)
    inter_length=np.arange(len(gradient))
    csd=spline(gradient,5,0)
    # 平滑化の処理をいれたい
    if is_gradient:
        csd = moving_average_for_time_direction(csd,average_size=gradient_size,mode="same")
    if is_standardized:
        csd = csd/np.max(np.abs(csd))
        vrange = 1
    x = np.linspace(xlim[0] , xlim[1], len(csd[0]))
    y = np.linspace( depth_range[0]+ch_distance/2, depth_range[1]-ch_distance/2, len(csd))
    X,Y=np.meshgrid(x,y[::-1])
    pcm=ax.pcolormesh(X,Y,csd,cmap="jet", shading="auto",vmax=vrange, vmin=-vrange,rasterized=True)
    if is_standardized:
        plt.colorbar(pcm,label="standalized csd")
    else:
        plt.colorbar(pcm,label="[mV/mm$^2$]")
    ax.set_ylim(ylim)
    ax.invert_yaxis()
    ax.set_yticks(np.arange(depth_range[0]+ch_distance,depth_range[1],ch_distance))
    ax.set_ylabel("depth [μm]")
    ax.set_xlabel("time from stimulation [ms]")
    
    return fig,ax

def plot_csd(lfp_data,channelmap,xlim,vrange,param,save_fig_dir_name,is_gradient = False,gradient_size = 5,axis=0,inverse=False,depth_range=[0,750],ch_distance= 50,is_standardized=False,ylim=[100,700]):
    '''
    inverse:bool 細胞外記録の値にしたい場合にはFalse, 細胞内記録の値にしたい場合にはTrue
    '''
    fig=plt.figure(facecolor="white")
    ax=fig.add_subplot(111)
    plot_csd_figure(fig,ax,lfp_data,channelmap,xlim,vrange,param,save_fig_dir_name,is_gradient = False,gradient_size = 5,axis=0,inverse=inverse,depth_range=depth_range,ch_distance= ch_distance,is_standardized=is_standardized,ylim=ylim)
    if not(os.path.exists("./csd_fig")):
        os.mkdir("./csd_fig")
    if not(os.path.exists(f"./csd_fig/{save_fig_dir_name}")):
        os.mkdir(f"./csd_fig/{save_fig_dir_name}")
    title=f"csd_{param}"
    plt.tight_layout()
    plt.savefig(f'./csd_fig/{save_fig_dir_name}/{title}.png')
    plt.cla()
    plt.clf()
    plt.close()
    gc.collect()
    
def plot_fourier_spectal_from_dic(dic,dir_name,xlim,samplerate):
    if not os.path.exists("./fourier_spectrum"):
        os.mkdir("./fourier_spectrum")
    if not os.path.exists(f"./fourier_spectrum/{dir_name}"):
        os.mkdir(f"./fourier_spectrum/{dir_name}")
    for key,value in dic.items():
        fig=plt.figure()
        ax=fig.add_subplot(111)
        ax.plot(111)
        point=len(value)
        d=1/samplerate
        F=np.fft.fft(value,n=point)
        freq=np.fft.fftfreq(n=point,d=d)
        Amp=np.abs(F/(point/2))
        left_point=np.where(freq==freq[freq>=xlim[0]][0])[0][0]
        right_point=np.argmax(freq[freq<=xlim[1]])
        xlim_point=[left_point,right_point]
        ax.plot(freq[xlim_point[0]:xlim_point[1]], Amp[xlim_point[0]:xlim_point[1]],color="k")
        ax.set_ylim(0,np.max(Amp[xlim_point[0]:xlim_point[1]]))
        ax.set_xlabel("Freqency [Hz]")
        ax.set_ylabel("Amplitude")
        if "\n" in key:
            title=key.replace("\n","")
        else:
            title=key
        ax.set_title(title)
        plt.savefig(f"./fourier_spectrum/{dir_name}/{title}.png")
        plt.cla()
        plt.clf()
        plt.close(fig)
        del ax,fig
        gc.collect()
    return

def plot_wave(axes,index,time_datas,volt_datas,xlim,title,is_single=False):
    if is_single:
        ax = axes
    else:
        row=index[0]
        col=index[1]
        ax=axes[row][col]
    time_datas=np.array(time_datas)
    ax.plot(time_datas,volt_datas,color="k")
    ax.set_xlim(xlim)
    if max(volt_datas)<=0.5:
        ax.set_ylim([-0.5,0.5])
    ax.set_xlabel("time from stimulation[ms]")
    ax.set_ylabel("voltage [V]")
    ax.set_title(title)

def plot_fft(axes,index,volt_datas,samplerate,xlim,title):
    #振幅スペクトルを描画する
    row=index[0]
    col=index[1]
    ax=axes[row][col]
    freq,Amp= acquire_amp_spectrum(volt_datas,samplerate)
    left_point=np.where(freq==freq[freq>=xlim[0]][0])[0][0]
    right_point=np.argmax(freq[freq<=xlim[1]])
    xlim_point=[left_point,right_point]
    ax.plot(freq[xlim_point[0]:xlim_point[1]], Amp[xlim_point[0]:xlim_point[1]],color="k")
    ax.set_xlabel("Freqency [Hz]")
    ax.set_ylabel("Amplitude")
    ax.set_title(title)
    

def plot_power_fft(axes,index,volt_datas,samplerate,xlim,title):
    #振幅スペクトルを描画する
    row=index[0]
    col=index[1]
    ax=axes[row][col]
    freq,Amp= acquire_power_spectrum(volt_datas,samplerate)
    left_point=np.where(freq==freq[freq>=xlim[0]][0])[0][0]
    right_point=np.argmax(freq[freq<=xlim[1]])
    xlim_point=[left_point,right_point]
    ax.plot(freq[xlim_point[0]:xlim_point[1]], Amp[xlim_point[0]:xlim_point[1]],color="k")
    ax.set_xlabel("Freqency [Hz]")
    ax.set_ylabel("Amplitude")
    ax.set_title(title)