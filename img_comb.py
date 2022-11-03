#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 09:42:43 2022

@author: Mouchen
@discription: image combine for 4 images
@note: image format follow bellow
        lo byte              hi byte
        [        0x00000004        ] msb, 4bytes
        [      image1 offset       ] msb, 4bytes
        [       image1 size        ] msb, 4bytes
        [      image2 offset       ] msb, 4bytes
        [       image2 size        ] msb, 4bytes
        [      image3 offset       ] msb, 4bytes
        [       image3 size        ] msb, 4bytes
        [      image4 offset       ] msb, 4bytes
        [       image4 size        ] msb, 4bytes
        padding to image1 offset with 0xFF
        [       image1 data        ]
        padding to image2 offset with 0xFF
        [       image2 data        ]
        padding to image3 offset with 0xFF
        [       image3 data        ]
        padding to image4 offset with 0xFF
        [       image4 data        ]
        padding based on 64k unit with 0xFF
        [      MD5 encryption      ] msb, 16bytes
"""
import json, os, sys, hashlib

APP_NAME = "IMAGES COMBINE SCRIPT"
APP_AUTH = "Mouchen"
APP_RELEASE_VER = "1.1.1"
APP_RELEASE_DATE = "2022.11.03"

IMG_NUM = 4
IMG_STORE = "./img/"
HEADER_SIZE = 36 # WITH 'byte'
CONFIG_FILE = "./config.txt"

"""
CONFIG file demo
"""
BLOCK_UNIT = 64 # with 'k'
OUTPUT_IMG_PATH = "output_img.bin"
EN_ENCRIPTION = "enable"
DEMO_IMG_PREFIX = "test_img"
DEMO_IMG_OFST_LST = [
    0x0 + HEADER_SIZE,
    0x4b000 + HEADER_SIZE,
    0x4b000*2 + HEADER_SIZE,
    0x4b000*3 + HEADER_SIZE
]

"""
PADDING MODE
    [0] Image offset set by config file
    [1] Image offset set by padding method
"""
COMB_MODE_FLAG = 0
IMG_GAP_BYTES_IN_PADDING_MODE = 16

"""
    =================================== COMMON LIBRARY ===================================
"""
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
    # Check list size
    if (len(img_size_lst)!=IMG_NUM or len(img_offset_lst)!=IMG_NUM or len(img_path_lst)!=IMG_NUM):
        return False

    for i in range(IMG_NUM):
        # Check offset greater than header size
        if img_offset_lst[i] < HEADER_SIZE:
            msg_hdr_print("e", "Image " + str(i) + " offset should >= header size " + str(HEADER_SIZE))
            return False
        if i:
            # Check offset legal
            if img_offset_lst[i] < (img_offset_lst[i-1] + img_size_lst[i-1]):
                msg_hdr_print("e", "Image " + str(i) + " offset should >= last image offset + size = " + str(img_offset_lst[i-1] + img_size_lst[i-1]))
                return False
    return True

def get_md5_from_file(file_path) -> str:
    hash_md5 = hashlib.md5()

    with open(file_path, "rb") as image:
        for chunk in iter(lambda: image.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()

def byte_to_k(byte_num):
    return round(byte_num/1024)

def gen_bytes(num, pad_size, pad_val_str, mode):
    hex_str = str(hex(num))
    hex_str = hex_str.replace("0x", "")

    output = []
    if not pad_size:
        return output

    if ( len(hex_str) ) > pad_size*2:
        return output

    # padding
    if len(hex_str) != pad_size*2:
        hex_str = pad_val_str*(pad_size*2 - len(hex_str)) + hex_str

    if mode == "msb":
        for i in range( 0, len(hex_str), 2 ):
            output.append( int(hex_str[i]+hex_str[i+1], 16) )
    elif mode == "lsb":
        for i in range( len(hex_str)-1, 0, -2 ):
            output.append( int(hex_str[i-1]+hex_str[i], 16) )

    return output

def TOOL_CONFIG_WR(mode, file):
    data = {}
    # Write File
    if mode == "W":        
        # COMMON CONFIG
        data['COMMON_CONFIG'] = []
        data['COMMON_CONFIG'].append({
            'block_unit': BLOCK_UNIT,
            'output_path': OUTPUT_IMG_PATH,
            'encryption': EN_ENCRIPTION
        })
        
        # IMAGE INFO
        data['IMG_CONFIG'] = []
        for i in range(len(DEMO_IMG_OFST_LST)):
            data['IMG_CONFIG'].append({
                'name': "IMG_" + str(i),
                'path': IMG_STORE + DEMO_IMG_PREFIX + str(i) + ".bin",
                'offset': hex(DEMO_IMG_OFST_LST[i])
            })
            
        with open(file, 'w') as outfile:
            json.dump(data, outfile, indent=4)
    
    # Read File
    elif mode == "R":
        with open(file) as json_file:
            data = json.load(json_file)
            
            # Colect <Common config>            
            COMMON_CFG = [ data['COMMON_CONFIG'][0]['block_unit'], data['COMMON_CONFIG'][0]['output_path'], data['COMMON_CONFIG'][0]['encryption'] ]
            
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

"""
    =================================== MAIN CODE ===================================
"""
if __name__ == '__main__':
    APP_HEADER()
    
    # [STEP0] Mode switch
    msg_hdr_print("s", "Mode select")
    msg_hdr_print("n", "[0] Create an demo config file.", "         ")
    msg_hdr_print("n", "[1] Combine images with offset in config file.", "         ")
    msg_hdr_print("n", "[2] Combine images automatic by padding offset.", "         ")
    msg_hdr_print("n", "* Note: [1]/[2] config file required!", "         ")
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
        msg_hdr_print("s", "Start combine images task by given offset.")
        COMB_MODE_FLAG = 0
    elif mode == '2':
        msg_hdr_print("s", "Start combine images task by padding offset with interval "
            + str(IMG_GAP_BYTES_IN_PADDING_MODE) + " bytes."
        )
        COMB_MODE_FLAG = 1
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
    en_encryption = 0

    # [STEP1] Read config file
    output = TOOL_CONFIG_WR('R', CONFIG_FILE)

    if len(output[1]) != IMG_NUM:
        msg_hdr_print("e", "Should given " + str(IMG_NUM) + " images config in config.txt!")
        sys.exit(0)

    msg_hdr_print("s", "Reading config file...", "\n")
    msg_hdr_print("n", "[Common config]")
    msg_hdr_print("n", "* block_unit:   "+str(output[0][0]))
    block_unit = output[0][0]*1024
    msg_hdr_print("n", "* output_path:  "+output[0][1])
    output_img_path = output[0][1]
    if output[0][2].lower() == "enable":
        msg_hdr_print("n", "* encryption:   enable")
        en_encryption = 1
    else:
        msg_hdr_print("n", "* encryption:   disable")
        en_encryption = 0

    msg_hdr_print("n", "[Image config]")
    for i in range(IMG_NUM):
        cur_img_path = output[1][i][0]
        cur_img_exist = is_file_exist(cur_img_path)
        if cur_img_exist:
            cur_img_size = is_binary(cur_img_path)
        if COMB_MODE_FLAG == 0:
            cur_img_ofst = output[1][i][1]
        else:
            if i == 0:
                cur_img_ofst = hex( HEADER_SIZE )
            else:
                cur_img_ofst = hex( offset_lst[i-1] + size_lst[i-1] + IMG_GAP_BYTES_IN_PADDING_MODE )

        msg_hdr_print("n", "* Img" + str(i) + ":")
        msg_hdr_print("n", "path:    " + cur_img_path, "       ")
        
        if not cur_img_exist:
            msg_hdr_print("n", "exist:   X", "       ")
            msg_hdr_print("n", "size:    X", "       ")
            err_flag = 1
            continue
        else:
            msg_hdr_print("n", "exist:   O", "       ")

        msg_hdr_print("n", "offset:  " + cur_img_ofst, "       ")

        if not cur_img_size:
            msg_hdr_print("n", "size:    None-binary/Empty file", "       ")
            err_flag = 1
            continue
        else:
            msg_hdr_print("n", "size:    "+str(byte_to_k(cur_img_size))+"k("+str(cur_img_size)+" bytes)", "       ")
            
        path_lst.append(cur_img_path)
        offset_lst.append(int(cur_img_ofst, 16))
        size_lst.append(cur_img_size)
    
    if err_flag:
        msg_hdr_print("e", "There's at least one image lost or file type error, please check it in dir "+IMG_STORE)
        sys.exit(0)
    
    if not is_file_size_legal(size_lst, offset_lst, path_lst):
        msg_hdr_print("e", "File size check failed, please check whether offset sets wrong!")
        sys.exit(0)
    
    # [STEP2] Add Header
    msg_hdr_print("s", "Adding header to image...", "\n")
    comb_data = []
    comb_data += gen_bytes(4, 4, "0", "msb")
    for img_idx in range(IMG_NUM):
        comb_data += gen_bytes(offset_lst[img_idx], 4, "0", "msb")
        comb_data += gen_bytes(size_lst[img_idx], 4, "0", "msb")

    # [STEP3] Combine images
    msg_hdr_print("s", "Start combine binary files...", "\n")
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
            for i in range(offset_lst[0] - len(comb_data)):
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

    # [STEP4] (optional)Add MD5 16bytes
    if en_encryption:
        msg_hdr_print("s", "Adding MD5 encryption bytes to image...", "\n")
        md5str = get_md5_from_file(output_img_path)
        for i in range( 0, 32, 2 ):
            comb_data.append( int(md5str[i] + md5str[i+1], 16) )

        with open(output_img_path, 'wb') as f:
            f.write(bytearray(comb_data))
    
    msg_hdr_print("s", "Image combine success with "+str(byte_to_k(len(comb_data)))+"k("+str(len(comb_data))+"b).", "\n")
    msg_hdr_print("n", 'Please check output file named "'+output_img_path+'"',"         ")
