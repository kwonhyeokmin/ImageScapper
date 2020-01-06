from bs4 import BeautifulSoup
import os
import os.path as osp
from tqdm import tqdm
import json
import uuid
from urllib.request import urlopen, Request
import logging
import config
import pandas as pd
from datetime import datetime


def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('[%(asctime)s %(levelname)s %(module)s]: %(message)s'))
    logger.addHandler(handler)
    return logger


def run():
    try:
        target = pd.read_csv(TARGET_PATH, encoding='latin1')[['English Name', 'Link']]
    except IOError as e:
        logger.error('Please locate data_for_scapping.csv file in target directory')
        raise IOError('Please locate data_for_scapping.csv file in target directory')
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    }
    result = {'person_nm': [], 'image_path': [], 'link': []}
    for i in target.index:
        person_nm, page_url = tuple(target.iloc[i])
        person_nm = person_nm.replace(' ', '_')

        soup = BeautifulSoup(urlopen(Request(url=page_url, headers=header)), 'html.parser')

        images = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
            images.append((link, Type))
        for j, (url, image_type) in enumerate(tqdm(images[:min(len(images), cfg.max_count)], desc=person_nm)):
            try:
                req = Request(url, headers=header)
                resp = urlopen(req)
                raw_image = resp.read()
                extension = image_type if image_type else 'jpg'
                if extension.lower() not in cfg.extensions:
                    continue
                file_name = uuid.uuid4().hex
                save_path = os.path.join(IMG_DIR, person_nm)
                if not osp.isdir(save_path):
                    os.mkdir(save_path)
                # Save image file
                with open(osp.join(save_path, '{}.{}'.format(file_name, extension)), 'wb') as image_file:
                    image_file.write(raw_image)

                result['person_nm'].append(person_nm)
                result['image_path'].append(osp.join('image', cfg.site_name, person_nm, '{}.{}'.format(file_name, extension)))
                result['link'].append(url)

            except Exception as e:
                logger.debug(str(url))
                continue

    # Save result
    df = pd.DataFrame.from_dict(result)
    now = datetime.now()
    date_time = now.strftime("%Y%m%d_%H:%M:%S")
    df.to_excel(osp.join(cfg.DATA_DIR, "{}.xlsx".format(date_time)), index=False)


if __name__ == '__main__':
    # Set logger
    logger = configure_logging()
    cfg = config

    # Set directory
    if not osp.isdir(cfg.TARGET_DIR):
        os.mkdir(cfg.TARGET_DIR)
    if not osp.isdir(cfg.IMG_DIR):
        os.mkdir(cfg.IMG_DIR)
    TARGET_PATH = osp.join(cfg.TARGET_DIR, 'data_for_scraping.csv')
    IMG_DIR = cfg.IMG_DIR
    # Application start
    run()