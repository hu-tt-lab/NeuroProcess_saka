import os
import numpy as np
from pathlib2 import Path


def convert_npy_to_compressed_npz(npy_root_dir:Path):
    npy_dirs=list(npy_root_dir.glob("*"))
    if not os.path.exists("./npz"):
        os.mkdir("./npz")
    for npy_dir in npy_dirs:
        if not os.path.exists(f"./npz/{npy_dir.name}"):
            os.mkdir(f"./npz/{npy_dir.name}")
        npy_files=list(npy_dir.glob("*"))
        for npy_file in npy_files:
            wave=np.load(npy_file,allow_pickle=True)
            np.savez_compressed(f"./npz/{npy_dir.name}/{npy_file.stem}",wave)
        
        