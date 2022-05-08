"""
作成した各種ライブラリを2022年4月時に坂上が使用している形で処理描画を行う部分
とりあえず困ったらここの関数使いましょう。
"""

# import original methods
from DataIO import *
from Filter import *
from MatProcessing import *
from OscilloProcessing import *
from Plot import plot_abr,plot_lfp,plot_csd,plot_fourier_spectal_from_dic
from Setting import *
from TDTProcessing import *

def get_abr_data_from_mat_file_dir(dir_path: Path):
    # 各波形から最大の振幅を取り出し、それを統計量として各加算回数による低下を描画
    # ファイルの取り出し
    setting_instance=PlotSetting()
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
    for plx_filepath in plx_filelist:
        print(plx_filepath.name)
        lfp_data=process_lfp_from_FP_ch(plx_filepath,50,350,setting_instance)
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

