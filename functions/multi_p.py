import os
import requests
import json
import pandas as pd
import sqlite3


worker_db_uri = r'worker_dbs/db_{}.json'


def update_db_filename(current_table):
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
