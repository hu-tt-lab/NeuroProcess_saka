# 使用するライブラリの読み込み
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import json
import os
import sys
import scipy.io
import matplotlib as mpl
import matplotlib.pyplot as plt
import statistics
import math
import gc


def addition_average(mat_data, order_table, trial, offset=50, onset=350):
    result_df = order_table.drop("trial", axis=1).sort_values(
        ["state", "amp", "duration"]).drop_duplicates().reset_index(drop=True)
    for i in range(1, 17):
        result_df[f"lfp_{str(i).zfill(2)}"] = 0
        result_df[f"lfp_{str(i).zfill(2)}"] = result_df[f"lfp_{str(i).zfill(2)}"].astype(
            "object")

    base_timestamp = mat_data["EVT02"]
    wave_data = [[] for _ in range(16)]

    for i in range(1, 17):
        fp_name = f"FP{str(i).zfill(2)}"
        each_channel_wave = mat_data[fp_name]
        each_channel_wave = list(
            each_channel_wave[j][0] for j in range(len(each_channel_wave)))
        fp_ts_name = f"FP{str(i).zfill(2)}_ts"
        each_start_time = mat_data[fp_ts_name]
        # 最初のEVT配列の各要素から開始時間を0に揃えるように値を引き、sampleing_rateの値に揃える
        # sampleing_rateが1000であるため、小数点3桁で丸めてsampleing_rateをかけて整数にする
        timestamp = list(int(round(
            base_timestamp[j][0]-each_start_time[0][0], 3)*1000) for j in range(len(base_timestamp)))
        index = 0
        for timepoint in timestamp:
            each_wave = np.array(
                each_channel_wave[timepoint-offset:timepoint+onset])
            # 波形の部分の保存方法を変更する
            # orderを波形ごと持ってきてresult_dfの各LFP保存カラム"LFP_n"(n=01,02,03....)に保存する
            wave_info = order_table.iloc[index]
            # 格納したい配列のindexを取得
            if wave_info["state"] == "click":
                res_ind = result_df.query(
                    f'db == "{wave_info["db"]}" & state == "{wave_info["state"]}"').index[0]
            elif wave_info["state"] == "us_burst":
                res_ind = result_df.query(
                    f'amp == "{wave_info["amp"]}" & PRF == "{wave_info["PRF"]}" & window == "{wave_info["window"]}" & pulse_duration == "{wave_info["pulse_duration"]}" & duration == "{wave_info["duration"]}"').index[0]
            elif wave_info["state"] == "us_cont":
                res_ind = result_df.query(
                    f'amp == "{wave_info["amp"]}" & window == "{wave_info["window"]}" & state == "{wave_info["state"]}" & duration == "{wave_info["duration"]}"').index[0]
            # 元々result_dicは0埋めしてあるのでwaveの格納有無を比較演算子にて判断
            if type(result_df.at[res_ind, f"lfp_{str(i).zfill(2)}"]) is int:
                result_df.at[res_ind, f"lfp_{str(i).zfill(2)}"] = each_wave
            else:
                result_df.at[res_ind, f"lfp_{str(i).zfill(2)}"] += each_wave
            index += 1
        # 加算平均して[μV]に直す
    for i in range(len(result_df)):
        for j in range(1, 17):
            result_df.at[i, f'lfp_{str(j).zfill(2)}'] /= trial
            result_df.at[i, f'lfp_{str(j).zfill(2)}'] *= 1000  # [uV]になおす
    return result_df


def convert_files_to_json(mat_list, order_list):
    for i in range(0, len(mat_list)):
        # ファイルの読み込み
        mat_filepath = f"./mat/{mat_list[i]}"
        order_filepath = f"./order/{order_list[i]}"
        mat_filename = mat_list[i][:-4]
        print(mat_filename)
        mat_data = scipy.io.loadmat(mat_filepath)
        order_table = pd.read_csv(order_filepath)
        # 加算回数の決定
        trial = max(order_table["trial"])+1
        # 結果配列の取得
        result_df = addition_average(mat_data, order_table, trial)
        json_path = f"./result_json/{mat_filename}.json"
        result_df.to_json(json_path, orient="records")
        del result_df
        gc.collect()


def main():
    if not(os.path.exists("./result_json")):
        os.mkdir("./result_json")
    mat_list = ["trial1.mat","deattached.mat","100min_after.mat","140min_after.mat"] 
    order_list = ["211129_1749_order.csv","211129_1842_order.csv","211129_2016_order.csv","211129_2049_order.csv"]
    convert_files_to_json(mat_list, order_list)
    print("completed")


if __name__ == "__main__":
    main()
