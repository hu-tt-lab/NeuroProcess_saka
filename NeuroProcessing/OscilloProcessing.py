import struct
from decimal import *
import csv
import gc
import math
import os
from tokenize import String

# Global variables
INT_BYTE_LEN = 4
DOUBLE_BYTE_LEN = 8
RESERVE_BYTE_LEN = 0x800-0x11c

TWO_PREC = '0.00'
FIVE_PREC = '0.00000'
TEN_PREC = '0.0000000000'
ELEV_PREC = '0.00000000000'


HORI_DIV_NUM = 14
VERT_DIV_CODE = 25
Magnitude = [10e-24,10e-21,10e-18,10e-15,\
             10e-12,10e-9,10e-6,10e-3,1,\
             10e3,10e6,10e9,10e12,10e15]

def deal_to_data_unit(f, para_num):
    if para_num == 1:
        stream = f.read(DOUBLE_BYTE_LEN)
        data = struct.unpack('d',stream)[0]
        stream = f.read(INT_BYTE_LEN)
        unit = struct.unpack('i',stream)[0]
        stream = f.read(INT_BYTE_LEN)
        para = data*Magnitude[unit]
    else:
        para = []
        for i in range(0,para_num):
            stream = f.read(DOUBLE_BYTE_LEN)
            data = struct.unpack('d',stream)[0]
            stream = f.read(INT_BYTE_LEN)
            unit = struct.unpack('i',stream)[0]
            stream = f.read(INT_BYTE_LEN)
            data_unit = data*Magnitude[unit]
            para.append(data_unit)
    return para
    
def deal_to_int(f, para_num):
    if para_num == 1:
        stream = f.read(INT_BYTE_LEN)
        para = struct.unpack('i',stream)[0]
    else:
        para = []
        for i in range(0,para_num):
            stream = f.read(INT_BYTE_LEN)
            data= struct.unpack('i',stream)[0]
            para.append(data)
    return para

def get_bit_from_byte(byData,bit):
    n0 = 1 if((byData & (1<<bit))== (1<<bit)) else 0
    return n0
    
def bin_to_csv(file,csv_filename,dir_name = None):
    """convert .bin file which is created by oscilloscope to .csv file 

    Args:
        file (str): file name to use
        csv_filename (str): the name that you want to save as .csv file
        dir_name (str): directory where you want to save csv file

    Returns: 
        Array : time and recorded voltages
    """
    try:
        f=open(file,'rb+')
        ch_state = deal_to_int(f, 4)
        ch_vdiv = deal_to_data_unit(f, 4)
        ch_ofst = deal_to_data_unit(f, 4)
        digit_state = deal_to_int(f, 17)
        hori_list = deal_to_data_unit(f, 2)
        wave_len = deal_to_int(f, 1)
        print(wave_len)
        sara = deal_to_data_unit(f, 1)
        di_wave_len = deal_to_int(f, 1)
        print(di_wave_len)
        di_sara = deal_to_data_unit(f, 1)
        reserve = f.read(RESERVE_BYTE_LEN)
        data = f.read()
    except IOError:
        print("Error: Can't find the bin file or read failed!")
    else:
        f.close()
        print('Read data from bin file finished!')
    
    if not(os.path.exists("./csv")):
        os.mkdir("./csv")
    dir_path="./csv/"
    
    if type(dir_name) is str:
        if not(os.path.exists(f"./csv/{dir_name}")):
            os.mkdir(f"./csv/{dir_name}")
        dir_path=f"./csv/{dir_name}/"
    
    ##--------------------get csv head------------------
    csv_len = [['Record Length']]
    csv_vdiv = [['Vertical Scale']]
    csv_ofst = [['Vertical Offset']]
    csv_tdiv = [['Horizontal Scale']]
    csv_sara = [['Sample Rate']]
    csv_para = [['Second']]
        
    ch_state_sum = 0
    for i in range(0, len(ch_state)):
        ch_state_sum += ch_state[i]
        if ch_state[i]:
            csv_vdiv[0].append('C{0}:{1}'.format(i+1, Decimal(str(ch_vdiv[i])).quantize(Decimal(TWO_PREC))))
            csv_ofst[0].append('C{0}:{1}'.format(i+1, Decimal(str(ch_ofst[i])).quantize(Decimal(FIVE_PREC))))
            csv_para[0].append('Volt')
    if ch_state_sum > 0:
        csv_len[0].append('Analog:{}'.format(wave_len))
        csv_sara[0].append('Analog:{}'.format(sara))
          
    csv_tdiv[0].append(Decimal(str(hori_list[0])).quantize(Decimal(TEN_PREC)))
   
    digit_state_sum = 0
    if digit_state[0]:
        for i in range(1, len(digit_state)):
            digit_state_sum += digit_state[i]
            if digit_state[i]:
                if 'Second' not in csv_para[0]:
                    csv_para[0].append('Second')
                csv_para[0].append('D{}'.format(i-1))
            else:
                pass
            
    if digit_state_sum > 0:
        csv_len[0].append('Digital:{}'.format(di_wave_len))
        csv_sara[0].append('Digital:{}'.format(di_sara))

    print('Writing to csv head...')
    with open(f"{dir_path}{csv_filename}",'a',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_len)    
        writer.writerows(csv_sara)
        writer.writerows(csv_vdiv)
        writer.writerows(csv_ofst)    
        writer.writerows(csv_tdiv)
        writer.writerows(csv_para)

    ##-------------------------converting law data------------------------------
    if len(data) >= 14e6 or wave_len >= 1E6:
        BLOCK_LEN = 1000000
        print('start to block')
    else:
        BLOCK_LEN = wave_len

    block_num = int(wave_len//BLOCK_LEN)
    last_block_len = wave_len%BLOCK_LEN
    div_flag = False
    if  last_block_len!= 0:
        block_num = block_num +1
        div_flag = True
    
    time_volt_data=[[] for _ in range(block_num)]
    for k in range(0,block_num):
        CH1_DATA_BLOCK = range(BLOCK_LEN*k,BLOCK_LEN*(k+1))
        if k == (block_num -1) and div_flag:
            CH1_DATA_BLOCK = range(BLOCK_LEN*k,BLOCK_LEN*k+last_block_len)
        print('BLOCK{0} {1} converting...'.format(k,CH1_DATA_BLOCK))
        csv_ch_time_volt = []
        #-------------------------analog data convert------------------------------
        print('analog converting...')
        for i in CH1_DATA_BLOCK:
            ch_state_num = 0
            volt = []
            time_data = float(-hori_list[0]*HORI_DIV_NUM/2+ i*(1/sara))
            for j in range(0,len(ch_state)):
                if ch_state[j]:
                    volt_data = int(data[i+ (ch_state_num * wave_len)]) 
                    a = (volt_data -128)*ch_vdiv[j]/VERT_DIV_CODE - ch_ofst[j]
                    volt.append(Decimal(str(a)).quantize(Decimal(FIVE_PREC)))
                    ch_state_num += 1
                else:
                    pass
            if ch_state_num > 0:
                volt.insert(0,Decimal(str(time_data)).quantize(Decimal(ELEV_PREC)))    
            csv_ch_time_volt.append(volt)
            
        #-------------------------copy data to csv------------------------------
        print('BLOCK{} writing to csv...'.format(k))    
        with open('test.csv','a',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_ch_time_volt)
            del csv_ch_time_volt
            gc.collect()
  