from bs4 import BeautifulSoup
import os
import os.path as osp
from tqdm import tqdm
import json
import uuid
from urllib.request import urlopen, Request
import logging
from config import Config
import pandas as pd
from datetime import datetime
from threading import Thread
import imghdr


def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('[%(asctime)s %(levelname)s %(module)s]: %(message)s'))
    logger.addHandler(handler)
    return logger


class Scrapper(object):

    def __init__(self, config, headers):
        self.config = config
        self.headers = headers
        self.result = {'person_nm': [], 'image_path': [], 'link': []}

    def _get_urls(self, url, headers):
        soup = BeautifulSoup(urlopen(Request(url=url, headers=headers)), 'html.parser')
        return soup

    def save_result(self):
        # Save result
        df = pd.DataFrame.from_dict(self.result)
        now = datetime.now()
        date_time = now.strftime("%Y%m%d_%H:%M:%S")
        df.to_excel(osp.join(cfg.DATA_DIR, "{}.xlsx".format(date_time)), index=False)

    def save_images(self, url, image_type, person_nm, save_path):
        try:
            req = Request(url, headers=self.headers)
            resp = urlopen(req, timeout=self.config.timeout)
            raw_image = resp.read()
            extension = image_type if image_type else 'jpg'
            if extension.lower() not in cfg.extensions:
                raise ValueError
            file_name = uuid.uuid4().hex
            # Save image file
            save_path = osp.join(save_path, '{}.{}'.format(file_name, extension))
            with open(save_path, 'wb') as image_file:
                image_file.write(raw_image)
            # Check valid image
            if not imghdr.what(save_path) in cfg.extensions:
                extension = imghdr.what(save_path)
                os.remove(save_path)
                raise ValueError

            self.result['person_nm'].append(person_nm)
            self.result['image_path'].append(
                osp.join('image', cfg.site_name, person_nm, '{}.{}'.format(file_name, extension))
            )
            self.result['link'].append(url)

        except ValueError as e:
            logger.debug('Invalid extension type: {}'.format(extension.lower()))
            return

        except TimeoutError as e:
            logger.debug('TimeoutError: {}'.format(str(url)))
            return

        except Exception as e:
            logger.debug('UnknownError: {}'.format(str(url)))
            return

    def run(self):
        try:
            target = pd.read_csv(TARGET_PATH, encoding='latin1')[['English Name', 'Link']]
        except IOError as e:
            logger.error('Please locate data_for_scapping.csv file in target directory')
            raise IOError('Please locate data_for_scapping.csv file in target directory')

        for i in tqdm(target.index, desc='scraping'):
            person_nm, page_url = tuple(target.iloc[i])
            person_nm = person_nm.replace(' ', '_')

            # make person folders
            save_path = os.path.join(IMG_DIR, person_nm)
            if not osp.isdir(save_path):
                os.mkdir(save_path)

            soup = self._get_urls(url=page_url, headers=self.headers)
            images = []  # contains the link for Large original images, type of  image
            for a in soup.find_all("div", {"class": "rg_meta"}):
                link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
                images.append((link, Type))

            for url, image_type in images[:min(len(images), cfg.max_count)]:
                thread = Thread(target=self.save_images, args=(url, image_type, person_nm, save_path))
                thread.start()


if __name__ == '__main__':
    # Set logger
    logger = configure_logging()
    cfg = Config()
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    }

    # Set directory
    if not osp.isdir(cfg.TARGET_DIR):
        os.mkdir(cfg.TARGET_DIR)
    if not osp.isdir(cfg.IMG_DIR):
        os.mkdir(cfg.IMG_DIR)

    TARGET_PATH = osp.join(cfg.TARGET_DIR, 'data_for_scraping.csv')
    IMG_DIR = cfg.IMG_DIR
    # Application start
    scraper = Scrapper(config=cfg, headers=headers)
    scraper.run()