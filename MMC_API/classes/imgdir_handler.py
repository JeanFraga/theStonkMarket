import sqlite3
from tinydb import TinyDB

import numpy as np
import pandas as pd

import os
import io
import json
import requests

from PIL import Image
from PIL.ImageOps import fit

import tqdm
import praw
import multiprocessing
from multiprocessing import current_process

from keras.preprocessing.image import ImageDataGenerator

from MMC_API.functions.utils import check_isDeleted
from MMC_API.functions.workerdb_compilers import update_status_col
from MMC_API.functions.constants import (
    IMGDIR_PATH,
    WORKER_DB_URI,
    NUM_WORKERS,
    DB_PATH
)

def download(lst):
    post_id, post_url = lst
    output_filename = os.path.join(IMGDIR_PATH, f"{post_id}.png")
    _data = {'id': post_id}

    try:
        with requests.get(post_url) as response, open(output_filename, 'wb') as out_file:
            img = Image.open(io.BytesIO(response.content))
            img.save(out_file, format='png')

        if check_isDeleted(output_filename):
            os.remove(output_filename)
            _data['status'] = 'deleted'
            worker_db.insert(_data)
        else:
            with open(output_filename, 'r+') as out_file:
                raw_img = Image.open(output_filename)
                img = fit(raw_img, (224, 224), Image.ANTIALIAS)
                img.save(output_filename, format='png')
            _data['status'] = output_filename
            worker_db.insert(_data)
    except:
        _data['status'] = 'error'
        worker_db.insert(_data)


def initializer():
    global worker_db
    worker_id = (int(current_process().name.split("-", 1)[1])-1) % NUM_WORKERS
    worker_db = TinyDB(WORKER_DB_URI.format(worker_id))


class Imgdir_Handler:
    def __init__(self, chunksize=100):

        self.id_column = 'id'
        self.imgurl_column = 'media'

        self.chunksize = chunksize
        self.current_ids = None
        self.tables = ['dankmemes_scoring']

        self.chunk_counter = -1

    def set_table(self, current_table):
        self.tables = [current_table]

    def set_tables(self, table_list):
        self.tables = table_list



    def imgdata_generator(self):
        return ImageDataGenerator(rescale=1./255).flow_from_directory(
            IMGDIR_PATH,
            target_size=(150, 150),
            batch_size=32,
            class_mode='binary'
        )

    def imgdir_generator(self):
        for table in self.tables:
            sql_str = f'''
                SELECT {self.id_column}, {self.imgurl_column}
                FROM {table}
                WHERE status IS NULL;
            '''
            with sqlite3.connect(DB_PATH) as db:
                df = pd.read_sql(sql_str, db)
            if df.empty:
                print("This table's status column is filled")
            else:
                self.current_ids = df[self.id_column].tolist()
                data = np.array(df)
                num_chunks = (len(data) // self.chunksize)

                for chunk in np.array_split(data, num_chunks):

                    filelist = [f for f in os.listdir(IMGDIR_PATH)]
                    if filelist:
                        for f in filelist:
                            os.remove(os.path.join(IMGDIR_PATH, f))

                    p = multiprocessing.Pool(NUM_WORKERS, initializer)
                    list(tqdm.tqdm(p.imap_unordered(
                        download, chunk), total=len(chunk)))
                    p.close()
                    p.join()

                    # update_status_col(table)

                    self.chunk_counter += 1

                    yield
