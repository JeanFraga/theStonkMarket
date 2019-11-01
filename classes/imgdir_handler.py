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

from functions.workerdb_compilers import update_status_col


def download(lst):
    imgdir_path = 'memes_imgdir'
    post_id, post_url = lst

    output_filename = os.path.join(
        imgdir_path, f"{post_id}.png")
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
    worker_db_uri = 'worker_dbs/db_{}.json'

    worker = (
        int(multiprocessing.current_process().name.split("-", 1)[1])-1) % 8

    db = TinyDB(worker_db_uri.format(worker))


class imgdir_handler:
    def __init__(self, chunksize=100):
        self.num_workers = 8

        self.db_path = "memes.db"
        self.imgdir_path = 'memes_imgdir'

        self.id_column = 'id'
        self.imgurl_column = 'media'

        self.chunksize = chunksize
        self.current_ids = None

        self.chunk_counter = -1

    def set_table(self, current_table):
        self.tables = [current_table]

    def set_tables(self, table_list):
        self.tables = table_list

    def imgdir_generator(self):
        for table in self.tables:
            sql_str = f'''SELECT {self.id_column}, {self.imgurl_column} FROM {table} WHERE status IS NULL'''
            with sqlite3.connect(self.db_path) as db:
                df = pd.read_sql(sql_str, db)
            if df.empty:
                print("This table's status column is filled")
            else:
                self.current_ids = df[self.id_column].tolist()
                data = np.array(df)
                num_chunks = (len(data) // self.chunksize)

                for chunk in np.array_split(data, num_chunks):

                    filelist = [f for f in os.listdir(self.imgdir_path)]
                    if filelist:
                        for f in filelist:
                            os.remove(os.path.join(self.imgdir_path, f))

                    p = multiprocessing.Pool(self.num_workers, initializer)
                    list(tqdm.tqdm(p.imap_unordered(
                        download, chunk), total=len(chunk)))
                    p.close()
                    p.join()

                    # update_status_col(table)

                    self.chunk_counter += 1

                    yield
