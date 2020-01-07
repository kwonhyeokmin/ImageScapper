import os
import os.path as osp


class Config:

    def __init__(self):
        ROOT_DIR = os.getcwd()
        # Driver path
        self.DRIVER_PATH = osp.join(ROOT_DIR, 'driver', 'chromedriver')
        # Data path
        self.DATA_DIR = osp.join(ROOT_DIR, 'data')
        self.TARGET_DIR = osp.join(self.DATA_DIR, 'target')
        self.IMG_DIR = osp.join(self.DATA_DIR, 'image')
        # src
        self.max_count = 100
        self.extensions = ['jpg', 'jpeg', 'png']
        self.site_name = 'google'
        self.timeout = 10000
