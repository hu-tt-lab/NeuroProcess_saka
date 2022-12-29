from typing import Union
from scipy import ndimage,interpolate,signal
import numpy as np
from scipy import fftpack
#bandpass_filterの設定
def bandpass(x, samplerate, fp, fs, gpass, gstop):
    fn = samplerate / 2                           #ナイキスト周波数
    wp = fp / fn                                  #ナイキスト周波数で通過域端周波数を正規化
    ws = fs / fn                                  #ナイキスト周波数で阻止域端周波数を正規化
    N, Wn = signal.buttord(wp, ws, gpass, gstop)  #オーダーとバターワースの正規化周波数を計算
    b, a = signal.butter(N, Wn, "band")           #フィルタ伝達関数の分子と分母を計算
    y = signal.filtfilt(b, a, x)                  #信号に対してフィルタをかける
    return y  
#バターワースフィルタ（ローパス）
def lowpass(x, samplerate, fp, fs, gpass, gstop):
    fn = samplerate / 2                           #ナイキスト周波数
    wp = fp / fn                                  #ナイキスト周波数で通過域端周波数を正規化
    ws = fs / fn                                  #ナイキスト周波数で阻止域端周波数を正規化
    N, Wn = signal.buttord(wp, ws, gpass, gstop)  #オーダーとバターワースの正規化周波数を計算
    b, a = signal.butter(N, Wn, "low")            #フィルタ伝達関数の分子と分母を計算
    y = signal.filtfilt(b, a, x)                  #信号に対してフィルタをかける
    return y 

#バターワースフィルタ(ハイパス)
def highpass(x, samplerate, fp, fs, gpass, gstop):
    fn = samplerate / 2                           #ナイキスト周波数
    wp = fp / fn                                  #ナイキスト周波数で通過域端周波数を正規化
    ws = fs / fn                                  #ナイキスト周波数で阻止域端周波数を正規化
    N, Wn = signal.buttord(wp, ws, gpass, gstop)  #オーダーとバターワースの正規化周波数を計算
    b, a = signal.butter(N, Wn, "high")            #フィルタ伝達関数の分子と分母を計算
    y = signal.filtfilt(b, a, x)                  #信号に対してフィルタをかける
    return y 

def notchpass(x,threshold,samplerate):
    """
    フーリエ変換を使用したノッチフィルタ

    :param x: 波形
    :param threshold: カットする周波数閾値，低周波/高周波の順に並んだものを受け取る
    """
    if threshold[0] > threshold[1]:
        raise ValueError()
    spectral = fftpack.fft(x, axis=0)
    index =  len(x)/samplerate* np.array(threshold)
    index = np.array(index,dtype="int64")
    spectral[index[0]:index[1]] = 0
    spectral[-index[1]:-index[0]] = 0
    return fftpack.ifft(spectral, axis=0).real

def source(wave, d: float=0.05, inverse = False):
    # 0.3は脳に置ける電流の伝導率
    if inverse:
        minus = -1
    else:
        minus = 1
    return minus* 0.3 * np.gradient(np.gradient(wave, axis=1), axis=1) / (d**2)

def gradient_double(wave,axis: int=0, coeff = -1):
    return coeff * np.gradient(np.gradient(wave, axis=axis), axis=axis)

def blur(reshape_data,size,axis):
    return ndimage.uniform_filter1d(reshape_data,size,axis)

def spline(reshape_data,size,axis: int=-1):
    x = np.arange(reshape_data.shape[axis])
    function = interpolate.interp1d(x, reshape_data, axis=axis)
    u = np.linspace(0, x[-1], (x.size - 1) * (size + 1) + 1)
    return function(u)

def acquire_amp_spectrum(voltage_data: Union[list,np.ndarray],samplerate:int,norm:str="backward"):
    point=len(voltage_data)
    d=1/samplerate
    F=np.fft.fft(voltage_data,n=point,norm=norm)
    freq=np.fft.fftfreq(n=point,d=d)
    Amp=np.abs(F)
    return freq,Amp


def acquire_power_spectrum(voltage_data: Union[list,np.ndarray],samplerate:int,norm:str = "backward"):
    freq,Amp = acquire_amp_spectrum(voltage_data, samplerate,norm)
    Amp=np.power(Amp,2)
    return freq,Amp

def moving_average_for_time_direction(waveform:Union[list,np.ndarray],average_size:int = 5, mode:str="valid"):
    if isinstance(waveform,list):
        waveform = np.array(waveform)
    moving_average = np.array([np.convolve(wave,np.ones(average_size)/average_size,mode=mode) for wave in waveform])
    return moving_average