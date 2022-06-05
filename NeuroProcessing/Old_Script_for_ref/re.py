from email.mime import base
import re

target_string="us_burst_158V_window_0_prf_1500Hz_pd_160us.mat"
# 文字列の付与部分をあとから追記するようにするほうがよさそう
base_info = re.search("us_burst_(\d+V)",target_string)
volt=base_info.group(1)
start=base_info.end()
if len(target_string)!=(start+4):
    param_info=target_string[start+1:-4]
    params=list(param_info.split("_"))
    dict= {}
    for i in range(len(params)//2):
        dict[params[2*i]]=params[2*i+1]
    print(dict)
print(volt)

def kwargs_test2(a,b,**kwargs):
    
    kwargs_test(a,b,**kwargs)

def kwargs_test(a="a",b="b",c="c",d="d"):
    print(a,b,c,d)

dict ={"c":"cc","d":"dd"}
kwargs_test2("aa","bb",**dict)