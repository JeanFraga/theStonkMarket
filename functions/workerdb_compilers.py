import os
import json
import pandas as pd
import sqlite3

from functions.sql import insert_meme_data
from functions.constants import WORKER_DB_URI

def clear_worker_dbs():
    for i in range(0, 8):
        try: os.remove(WORKER_DB_URI.format(i))
        except: pass

def insert_new_data(current_table):
    cdf = pd.DataFrame()
    for i in range(0, 8):
        with open(WORKER_DB_URI.format(i), "r") as data:
            json_data = json.load(data)

        df = pd.DataFrame.from_dict(json_data['_default']).transpose()
        cdf = pd.concat([cdf, df], ignore_index=True, axis=0, sort=True)
        os.remove(WORKER_DB_URI.format(i))

    with sqlite3.connect(os.environ['DB_PATH']) as db:
        data = list(cdf.itertuples(index=False, name=None))
        db.cursor().executemany(insert_meme_data(current_table, list(cdf)), data)


def update_status_col(current_table):
    cdf = pd.DataFrame(columns=['id', 'status'])
    for i in range(0, 8):
        with open(WORKER_DB_URI.format(i), "r") as data:
            json_data = json.load(data)
        os.remove(WORKER_DB_URI.format(i))

        df = pd.DataFrame.from_dict(json_data['_default']).transpose()
        cdf = pd.concat([cdf, df], ignore_index=True, axis=0, sort=False)

    sql_str = f'''UPDATE {current_table}
                SET status = ?
                WHERE id = ?; '''

    with sqlite3.connect(os.environ['DB_PATH']) as db:
        data = list(cdf[['status', 'id']].itertuples(index=False, name=None))
        db.cursor().executemany(sql_str, data)
