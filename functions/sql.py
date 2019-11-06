import sqlite3
import time
from datetime import datetime
import time
import pandas as pd
import os
from functions.constants import MONTH_TD, LAG_15MIN, DB_PATH

memedata_schema = """
    id TEXT,
    title TEXT,
    author TEXT,
    media TEXT,
    meme_text TEXT,
    status TEXT,
    timestamp INTEGER,
    datetime DATETIME,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    hour INTEGER,
    minute INTEGER,
    upvote_ratio FLOAT,
    upvotes INTEGER,
    downvotes INTEGER,
    nsfw BOOL,
    num_comments INTEGER
"""

def set_time_range(table, year, month, day=1, hour=0, minute=0):
    dt = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    fresh_month_ts = time.mktime(dt.timetuple())

    max_db_time = get_max_timestamp(table)
    if not max_db_time:
        max_db_time = fresh_month_ts

    if month == 12:
        next_month = 1
        year += 1
    else:
        next_month = month+1

    dt = datetime(year=year, month=next_month, day=day, hour=hour, minute=minute)
    next_month_ts = time.mktime(dt.timetuple())

    return max_db_time, next_month_ts

def table_prep(table, cols=''):
    with sqlite3.connect(DB_PATH) as db:
        exists = db.cursor().execute(check_table_exists(table)).fetchall()
    if not exists:
        create_table(table, cols=cols)
        return True
    return False

def get_max_timestamp(table):
    max_ts_str = f'''SELECT MAX(timestamp) FROM {table}'''
    with sqlite3.connect(DB_PATH) as db:
        max_db_time = db.cursor().execute(max_ts_str)
        return max_db_time.fetchall()[0][0]

def get_scoring_df(subreddit):
    now= int(time.time() - LAG_15MIN)
    data_table = f'{subreddit}_scoring'
    select_latest_month = f"""
        Select *
        FROM {data_table}
        WHERE timestamp > {now-MONTH_TD}
    """
    with sqlite3.connect(DB_PATH) as db:
        return pd.read_sql(select_latest_month, db)

def insert_meme_data(table, cols):
    col_ord_str = str(cols)[1:-1].replace("'", "")
    return f''' INSERT INTO {table}({col_ord_str}) VALUES({','.join(['?']*len(cols))}) '''

def get_meme_data(table, cols, condition):
    if cols == '*':
        return f''' SELECT *
                    FROM {table}
                    WHERE {condition}
                '''
    col_ord_str = str(cols)[1:-1].replace("'", "")
    return f''' INSERT INTO {table}({col_ord_str}) VALUES({','.join(['?']*len(cols))}) '''

def check_table_exists(table):
    return f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"""

def get_table_list():
    db_list = []
    with sqlite3.connect(DB_PATH) as db:
        for db_name in db.cursor().execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
            db_list.append(db_name[0])
    return db_list

def remove_duplicates(table):
    delete_dups_str = f"""
        DELETE FROM {table}
        WHERE rowid NOT IN (
            SELECT min(rowid)
            FROM {table}
            GROUP BY id
        ); 
    """

    with sqlite3.connect(DB_PATH) as db:
        db.cursor().execute(delete_dups_str)

def remove_dups_all_tables():
    db_list = get_table_list()
    for db_name in db_list:
        remove_duplicates(db_name)

def create_table(name, cols=''):
    if not cols:
        global memedata_schema
        cols = memedata_schema

    sql_create_table = f'CREATE TABLE IF NOT EXISTS {name}(' + cols + ');'

    with sqlite3.connect(DB_PATH) as db:
        db.cursor().execute(sql_create_table)
