#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 09:42:43 2022

@author: mouchen
"""
import json, os, sys

APP_NAME = "IMAGES COMBINE SCRIPT"
APP_AUTH = "Mouchen"
APP_RELEASE_VER = "1.0.0"
APP_RELEASE_DATE = "2022.02.22"

IMG_NUM = 4
IMG_STORE = "./img/"
OFFSET_LST = [0x0, 0x4b000, 0x4b000*2, 0x4b000*3]
BLOCK_UNIT = 64 # with 'k'
CONFIG_FILE = "./config.txt"
OUTPUT_IMG_PATH = "output_img.bin"
    
def msg_hdr_print(hdr_type, msg, pre_msg=""):
    if hdr_type == "s":     #system
        header = "<system> "
    elif hdr_type == "w":   #warning
        header = "<warn> "
    elif hdr_type == "e":   #error
        header = "<error> "
    elif hdr_type == "wdt": #watchdog
        header = "<wdt> "
    elif hdr_type == "n": #none
        header = ""
    print(pre_msg + header + msg)

def is_file_exist(file_path):
    if not os.path.exists(file_path):
        return False
    else:
        return True

def is_binary(file_path):
    try:
        with open(file_path, 'tr') as check_file:
            check_file.read()
            return 0
    except:
        return os.path.getsize(file_path)

def is_file_size_legal(img_size_lst, img_offset_lst, img_path_lst):
    if (len(img_size_lst)!=IMG_NUM or len(img_offset_lst)!=IMG_NUM or len(img_path_lst)!=IMG_NUM):
        return False
    return True

def byte_to_k(byte_num):
    return round(byte_num/1024)

def TOOL_CONFIG_WR(mode, file):
    data = {}
    # Write File
    if mode == "W":        
        # COMMON CONFIG
        data['COMMON_CONFIG'] = []
        data['COMMON_CONFIG'].append({
            'block_unit': BLOCK_UNIT,
            'output_path': OUTPUT_IMG_PATH
        })
        
        # IMAGE INFO
        data['IMG_CONFIG'] = []
        for i in range(len(OFFSET_LST)):
            data['IMG_CONFIG'].append({
                'name': "IMG_"+str(i),
                'path': IMG_STORE + "test_img"+str(i)+".bin",
                'offset': hex(OFFSET_LST[i])
            })
            
        with open(file, 'w') as outfile:
            json.dump(data, outfile, indent=4)
    
    # Read File
    elif mode == "R":
        with open(file) as json_file:
            data = json.load(json_file)
            
            # Colect <Common config>            
            COMMON_CFG = [ data['COMMON_CONFIG'][0]['block_unit'], data['COMMON_CONFIG'][0]['output_path'] ]
            
            # Colect <Img config>            
            IMG_CFG = []
            for i in range(len(data['IMG_CONFIG'])):
                IMG_CFG.append([ data['IMG_CONFIG'][i]['path'], data['IMG_CONFIG'][i]['offset'] ])
            
            PACKAGE_CONFIG = [
                COMMON_CFG,
                IMG_CFG
            ]
            
            return PACKAGE_CONFIG

def APP_HEADER():
    msg_hdr_print("n", "========================================================")
    msg_hdr_print("n", "* APP name:    "+APP_NAME)
    msg_hdr_print("n", "* APP auth:    "+APP_AUTH)
    msg_hdr_print("n", "* APP version: "+APP_RELEASE_VER)
    msg_hdr_print("n", "* APP date:    "+APP_RELEASE_DATE)
    msg_hdr_print("n", "========================================================")

if __name__ == '__main__':
    APP_HEADER()
    
    # [STEP0] Mode switch
    msg_hdr_print("s", "Mode select")
    msg_hdr_print("n", "[0] Create an demo config file.", "         ")
    msg_hdr_print("n", "[1] Combine images if config.txt already exist.", "         ")
    mode = input(">> mode: ")
    if mode == '0':
        msg_hdr_print("s", "Start create demo config file.")
        if not is_file_exist(IMG_STORE):
            msg_hdr_print("s", 'Folder "'+IMG_STORE+'" not exist, creating it...')
            os.mkdir(IMG_STORE)

        TOOL_CONFIG_WR('W', CONFIG_FILE)
        msg_hdr_print("s", "Demo config file create success!")
        msg_hdr_print("n", 'Please modify contents by following "README.txt"!', "         ")
        msg_hdr_print("n", 'Please add 4 images into "'+IMG_STORE+'"!', "         ")
        sys.exit(0)
    elif mode == '1':
        msg_hdr_print("s", "Start combine images task.")
    else:
        msg_hdr_print("w", "No such mode!")
        sys.exit(0)
            
    if not is_file_exist(CONFIG_FILE):
        msg_hdr_print("e", "Config file not found, please create it first!")
        sys.exit(0)
    
    err_flag = 0
    path_lst = []
    offset_lst = []
    size_lst = []
    block_unit = 0
    output_img_path = ""
    
    # [STEP1] Read config file
    output = TOOL_CONFIG_WR('R', CONFIG_FILE)
    
    msg_hdr_print("s", "Reading config file...", "\n")
    msg_hdr_print("n", "[Common config]")
    msg_hdr_print("n", "* block_unit:   "+str(output[0][0]))
    block_unit = output[0][0]*1024
    msg_hdr_print("n", "* output_path:  "+output[0][1])
    output_img_path = output[0][1]
    
    msg_hdr_print("n", "[Image config]")
    for i in range(IMG_NUM):
        msg_hdr_print("n", "* Img"+str(i)+":")
        msg_hdr_print("n", "path:    "+output[1][i][0], "       ")
        msg_hdr_print("n", "offset:  "+str(output[1][i][1]), "       ")
        
        if not is_file_exist(output[1][i][0]):
            msg_hdr_print("n", "exist:   X", "       ")
            msg_hdr_print("n", "size:    X", "       ")
            err_flag = 1
            continue
        else:
            msg_hdr_print("n", "exist:   O", "       ")
            
        f_size = is_binary(output[1][i][0])
        if not f_size:
            msg_hdr_print("n", "size:    None-binary/Empty file", "       ")
            err_flag = 1
            continue
        else:
            msg_hdr_print("n", "size:    "+str(byte_to_k(f_size))+"k("+str(f_size)+"b)", "       ")
            
        path_lst.append(output[1][i][0])
        offset_lst.append(int(output[1][i][1], 16))
        size_lst.append(f_size)
    
    if err_flag:
        msg_hdr_print("e", "There's at least one image lost or file type error, please check it in dir "+IMG_STORE)
        sys.exit(0)
    
    if not is_file_size_legal(size_lst, offset_lst, path_lst):
        msg_hdr_print("e", "File size check failed, please check whether offset sets wrong!")
        sys.exit(0)
    
    # [STEP2] Combine images
    msg_hdr_print("s", "Start combine binary files...", "\n")
    comb_data = []
    for img_idx in range(IMG_NUM):
        msg_hdr_print("n", "Combine Img_"+str(img_idx)+"...", "         ")
        
        # check whether image offset set wrong
        if offset_lst[img_idx] < len(comb_data):
            msg_hdr_print("e", "Img_"+str(img_idx)+" offset should >= "+str(len(comb_data)))
            sys.exit(0)

        with open(path_lst[img_idx],"rb") as f:
            data = f.read()
        
        # if first image start with non-zeror offset, need to pad first
        if not img_idx:
            for i in range(offset_lst[0]):
                comb_data.append(0xff)
        
        # append image
        for i in range(len(data)):
            comb_data.append(data[i])
        
        # append backward padding
        if (img_idx+1) == 4:
            add_num = block_unit - ( len(comb_data)%block_unit )
        else:
            add_num = offset_lst[img_idx+1]-len(comb_data)

        for i in range(add_num):
            comb_data.append(0xff)
    
    with open(output_img_path, 'wb') as f:
        f.write(bytearray(comb_data))
    
    msg_hdr_print("s", "Image combine success with "+str(byte_to_k(len(comb_data)))+"k("+str(len(comb_data))+"b).", "\n")
    msg_hdr_print("n", 'Please check output file named "'+output_img_path+'"',"         ")
    
