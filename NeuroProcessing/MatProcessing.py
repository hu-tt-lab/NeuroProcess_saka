import numpy as np

def diff_by_block(base,compare,block_size):
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