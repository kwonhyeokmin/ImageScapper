import os
import os.path as osp

ROOT_DIR = os.getcwd()
# Driver path
DRIVER_PATH = osp.join(ROOT_DIR, 'driver', 'chromedriver')
# Data path
DATA_DIR = osp.join(ROOT_DIR, 'data')
TARGET_DIR = osp.join(DATA_DIR, 'target')
IMG_DIR = osp.join(DATA_DIR, 'image')
# src
max_count = 100
extensions = ['jpg', 'jpeg', 'png']
site_name = 'google'
