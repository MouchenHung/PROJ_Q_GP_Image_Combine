# PROJ_Q_GP_Image_Combine
Combine 4 image to 1 images by following config file.

### Purpose:
    Script to combine 4 images to 1 image in project GP.

### First rlease date:
    2022.02.22

### Version: 
- 1.0 - First commit - 2022/02/22
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
           --> python img_comb.py --> choose mode[0]
           
  - **STEP2. Modify config file**
    - block_unit: Suppoment byte numbers for last image
    - output_path: Final combine-image path
    - name: One image name(should not modify!)
    - path: One image path
    - offset: One image start offset(This might cause some problem if set in wrong address)

  - **STEP3. Run**\
           --> python img_comb.py --> choose mode[1]

### Note
- 1: Please choose mode[0] to create folder ***./img*** and demo config file ***config.txt*** if first using this APP.
- 2: Only need to modify ***config.txt*** and choose mode[1] after finished mode[0].
- 3: Images in ***./img*** folder is just demo, please add your own images into it.
- 4: Images must only put in ***./img*** folder.
