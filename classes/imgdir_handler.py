import sqlite3
from tinydb import TinyDB

import numpy as np
import pandas as pd

import os
import io
import json
import requests

from PIL import Image
from PIL import ImageChops
from cv2 import cv2

import tqdm
import praw
import multiprocessing

from tinydb import TinyDB

from functions.multi_p import update_db_filename

NUM_WORKERS = 8
worker_worker_db_uri = 'worker_dbs/db_{}.json'
OUT_DIR = 'memes_imgdir'


class imgdir_handler:
    def __init__(self, db_path, chunksize=10_000):
        self.chunksize = chunksize
        self.db_path = db_path

        self.chunk_counter = -1

    def set_table(self, current_table):
        self.tables = [current_table]

    def set_tables(self, table_list):
        self.tables = table_list

    def imgdir_generator(self):
        def download(lst):
            post_id, post_url = lst
            output_filename = os.path.join(
                OUT_DIR, f"{post_id}.png")
            _data = {
                'id': post_id
            }

            if not os.path.isfile(output_filename):
                try:
                    with requests.get(post_url) as response, open(output_filename, 'wb') as out_file:
                        i = Image.open(io.BytesIO(response.content))
                        i.save(out_file, format='png')

                    deleted = cv2.imread('assets/image404.png')
                    deleted_nb = cv2.imread('assets/image404_nb.png')
                    image = cv2.imread(output_filename)

                    try:
                        diff = cv2.subtract(image, deleted)
                    except:
                        diff = True
                    try:
                        diff_nb = cv2.subtract(image, deleted_nb)
                    except:
                        diff_nb = True

                    isDeleted = np.all(diff == 0) | np.all(diff_nb == 0)

                    if not isDeleted:
                        _data['status'] = output_filename
                        db.insert(_data)
                    else:
                        os.remove(output_filename)
                        _data['status'] = 'deleted'
                        db.insert(_data)

                except:
                    _data['status'] = 'error'
                    db.insert(_data)

        def initializer():

            global db
            global worker_worker_db_uri

            worker = (
                int(multiprocessing.current_process().name.split("-", 1)[1])-1) % 8

            db = TinyDB(worker_worker_db_uri.format(worker))

        for table in self.tables:
            sql_str = f'''SELECT id, media FROM {table} WHERE status IS NULL'''
            with sqlite3.connect(self.db_path) as db:
                df = pd.read_sql(sql_str, db)
            if df.empty:
                print("This table's status column is filled")
            else:
                data = np.array(df)
                num_chunks = (len(data)//self.chunksize)

                for chunk in np.array_split(data, num_chunks):
                    p = multiprocessing.Pool(NUM_WORKERS, initializer)
                    list(tqdm.tqdm(p.imap_unordered(
                        download, chunk), total=len(chunk)))
                    p.close()
                    p.join()

                    update_db_filename(table)

                    self.chunk_counter += 1

                    yield
