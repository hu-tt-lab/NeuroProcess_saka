from fileinput import filename
import os
import re
from path import Path


from pathlib import Path

single_dir = "Y:/Sakagami/20220506_fg_voltage/bin/06_us_burst_freq_500kHz_prf_1500Hz_pulse_1-100/"
single_dir_path=Path(single_dir)
bin_files = list(single_dir_path.glob("*"))
#print(*bin_files[:10],sep="\n")
#print("----------")
#print(*bin_files[-10:],sep="\n")
day="2022-05-06"

if len(bin_files) >= 100:
    zfill_num=3
else:
    zfill_num=2
# file名を0埋め
num_after_100=101
for bin_file in bin_files:
    try:
        if day in bin_file.name:
            num=str(num_after_100).zfill(zfill_num)
            num=f"({num})"
            date_info=re.search(f"- {day}T[0-9]+.[0-9]+",bin_file.name).group(0)
            os.rename(bin_file,f"{bin_file.parent}\{bin_file.name.replace(date_info,num)}")
            num_after_100+=1
        else:
            num=re.search("[0-9]+",bin_file.name).group(0)
            os.rename(bin_file,f"{bin_file.parent}\{bin_file.name.replace(num,str(num).zfill(zfill_num))}")
    except:
        num="0".zfill(zfill_num)
        num=f"({num})"
        os.rename(bin_file,f"{bin_file.parent}\{bin_file.name.replace('.bin',' '+num+'.bin')}")

# num_after_100=103
# print(len(bin_files))
# for bin_file in bin_files:
#     try:
#         if str(num_after_100) in bin_file.name:
#             num=str(num_after_100-1).zfill(zfill_num)
#             date_info=re.search(f"usr_wf_data \(([0-9]+)\)",bin_file.name).group(1)
#             print(date_info)
#             os.rename(bin_file,f"{bin_file.parent}\{bin_file.name.replace(date_info,num)}")
#             num_after_100+=1
#     except:
#         continue