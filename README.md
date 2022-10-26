# PROJ_Q_GP_Image_Combine
Combine 4 image to 1 images by following config file.

### Purpose:
    Script to combine 4 images to 1 image in project GP.

### First rlease date:
    2022.02.22

### Version:
- 1.1.0 - 2022/10/26
  - Feature:
    - Add header to output image with 36bytes
      - [Byte04:01(msb)]  Numbers of image
      - [Byte08:05(msb)]  Image1 offset
      - [Byte12:09(msb)]  Image1 size
      - [Byte16:13(msb)]  Image2 offset
      - [Byte20:17(msb)]  Image2 size
      - [Byte24:21(msb)]  Image3 offset
      - [Byte28:25(msb)]  Image3 size
      - [Byte32:29(msb)]  Image4 offset
      - [Byte36:33(msb)]  Image4 size
    - Add MD5 as last 16 bytes
      - [ByteN-16:N(msb)] 16bytes of MD5
  - Bug: none
- 1.0.0 - First commit - 2022/02/22
  - Feature: none
  - Bug: none

### Required:
- OS
  - Linux: support
  - Windows: support
- Enviroment
  - python(version requirement not sure yet!)

  Note: Given path should include "./img/"!

### Usage
  - **STEP1. Create a demo config file**\
           --> python img_comb.py --> choose mode[0]\
           ![alt text](./demo_img/demo_mode[0].png "MODE[0]")
           
  - **STEP2. Modify config file**
    - block_unit: Output image's block unit for last image padding, using k(1024b) as base
    - output_path: Final combine-image path
    - name: One image name(should not modify!)
    - path: One image path
    - offset: One image start offset(This might cause some problem if set in wrong address)

  - **STEP3. Run**\
           --> python img_comb.py --> choose mode[1]\
           ![alt text](./demo_img/demo_mode[1].png "MODE[1]")

### Note
- 1: Please choose mode[0] to create folder ***./img*** and demo config file ***config.txt*** if first using this APP.
- 2: Only need to modify ***config.txt*** and choose mode[1] after finished mode[0].
- 3: Images in ***./img*** folder is just demo, please add your own images into it.
- 4: Images must only put in ***./img*** folder.
