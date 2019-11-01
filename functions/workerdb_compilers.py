import os
import requests
import json
import pandas as pd
import sqlite3

from functions.sql import insert_meme_sql_string


worker_db_uri = r'worker_dbs/db_{}.json'

def insert_new_data(current_table):
    columns = ['id', 'title', 'author', 'timestamp', 'media', 'meme_text', 'status', 'datetime', 'year',
               'month', 'day', 'hour', 'minute', 'upvote_ratio', 'upvotes', 'downvotes', 'nsfw', 'num_comments']
    cdf = pd.DataFrame(columns=columns)
    for i in range(0, 8):
        with open(worker_db_uri.format(i), "r") as data:
            json_data = json.load(data)
        os.remove(worker_db_uri.format(i))

        df = pd.DataFrame.from_dict(json_data['_default']).transpose()
        cdf = pd.concat([cdf, df], ignore_index=True, axis=0, sort=True)

    
    with sqlite3.connect("memes.db") as db:
        data = list(cdf.itertuples(index=False, name=None))
        db.cursor().executemany(insert_meme_sql_string(current_table, list(cdf)), data)

def update_status_col(current_table):
    cdf = pd.DataFrame(columns=['id', 'status'])
    for i in range(0, 8):
        with open(worker_db_uri.format(i), "r") as data:
            json_data = json.load(data)
        os.remove(worker_db_uri.format(i))

        df = pd.DataFrame.from_dict(json_data['_default']).transpose()
        cdf = pd.concat([cdf, df], ignore_index=True, axis=0, sort=False)

    sql_str = f'''UPDATE {current_table}
                SET status = ?
                WHERE id = ?; '''

    with sqlite3.connect("memes.db") as db:
        data = list(cdf.iloc[:, ::-1].itertuples(index=False, name=None))
        db.cursor().executemany(sql_str, data)
