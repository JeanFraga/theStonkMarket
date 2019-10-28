import shutil
import subprocess
import sqlite3
from sqlite3 import Error
from tinydb import TinyDB, Query, where
from urllib.request import urlopen
from urllib.parse import urlparse

import math
import numpy as np
import pandas as pd
import itertools

import os
import glob
import io
import json
import time
import requests
from PIL import Image
from PIL import ImageChops
from cv2 import cv2

import tqdm
import praw
import multiprocessing

from datetime import datetime, timedelta
from tinydb import TinyDB, Query

from timeit import timeit

NUM_WORKERS = 8
db_uri = r'db_{}.json'


def compile_data(current_table):
    '''
    compiles each db from each worker into one db
    delete the worker dbs
    compile data into csv also
    '''
    cdf = pd.DataFrame(columns=['id', 'filename'])
    for i in range(0, 8):
        with open(db_uri.format(i), "r") as data:
            json_data = json.load(data)
        os.remove(db_uri.format(i))

        df = pd.DataFrame.from_dict(json_data['_default']).transpose()
        cdf = pd.concat([cdf, df], ignore_index=True, axis=0, sort=False)

    sql_str = f'''UPDATE {current_table}
                SET filename = ?
                WHERE id = ?; '''

    with sqlite3.connect("memes.db") as db:
        data = list(cdf.iloc[:, ::-1].itertuples(index=False, name=None))
        db.cursor().executemany(sql_str, data)


def download(lst):
    post_id, post_url = lst
    output_filename = os.path.join(
        f'memes_imgdir/month_{1}', f"{post_id}.png")

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

            same = np.all(diff == 0) | np.all(diff_nb == 0)
            if not same:
                _data = {
                    "filename": output_filename,
                    'id': post_id
                }
                db.insert(_data)
            else:
                os.remove(output_filename)
                _data = {
                    "filename": 'deleted',
                    'id': post_id
                }
                db.insert(_data)

        except:
            data = {
                'filename': 'error',
                'id': post_id
            }
            db.insert(data)


# give each pool worker its own db and reddit instance
def initializer():

    global db
    global db_uri

    worker = (
        int(multiprocessing.current_process().name.split("-", 1)[1])-1) % 8

    db = TinyDB(db_uri.format(worker))


def main():
    for i in range(1, 2):
        current_table = f'month_{i}'
        sql_str = f'''SELECT id, media FROM {current_table} WHERE filename IS NULL'''
        with sqlite3.connect("memes.db") as db:
            df = pd.read_sql(sql_str, db)
        if df.empty:
            continue
        else:
            data = np.array(df)
            chunksize = (len(data)//2_000) if (len(data) > 10_000) else 2

            for chunk in np.array_split(data, chunksize):

                p = multiprocessing.Pool(NUM_WORKERS, initializer)
                list(tqdm.tqdm(p.imap_unordered(download, chunk), total=len(chunk)))
                p.close()
                p.join()

                compile_data(current_table)


if __name__ == "__main__":
    main()
