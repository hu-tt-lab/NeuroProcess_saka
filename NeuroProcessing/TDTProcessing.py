import pandas as pd
import warnings

def read_tdtcsv(filename):
    df=pd.read_csv(filename)
    row=df.shape[0]
    column=df.shape[1]
    data_head=df.columns.get_loc("1")
    waveforms = {}
    dB_name=df.columns[df.columns.str.contains("\\(dB\\)")].values[0]

    if(row==len(set([f"{i}{j}" for i,j in zip(df["Sub. ID"], df[dB_name])]))):
        datanames=[f"{i}dB" for i in df[dB_name]]
    else:
        datanames=[f"{i} {j}dB-{k}" for i,j,k in zip(df["Sub. ID"], df[dB_name], df["Rec No."])]
        warnings.warn(f"音圧でデータを区別できません、同一の音圧データが含まれています")
    for i,j in enumerate(datanames):
        waveforms[j] = list(df.iloc[i,[*list(range(data_head,column-1))]])
    return waveforms

