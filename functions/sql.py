import sqlite3
import time
from datetime import datetime
import time
import pandas as pd
import os
from functions.constants import MONTH_TD, LAG_15MIN

def set_time_range(current_table, year, month):
    dt = datetime(year=year, month=month, day=1, hour=0, minute=0)
    fresh_month_ts = time.mktime(dt.timetuple())

    max_db_time = get_max_timestamp(current_table)
    if not max_db_time:
        max_db_time = fresh_month_ts

    if month == 12:
        next_month = 1
        year += 1
    else:
        next_month = month+1

    dt = datetime(year=year, month=next_month, day=1, hour=0, minute=0)
    next_month_ts = time.mktime(dt.timetuple())

    return max_db_time, next_month_ts

def table_prep(current_table, cols=''):
    with sqlite3.connect(os.environ['DB_PATH']) as db:
        exists = db.cursor().execute(check_table_exists(current_table)).fetchall()
    if not exists:
        create_table(current_table, cols=cols)
        return True
    return False

def get_max_timestamp(current_table):
    max_ts_str = f'''SELECT MAX(timestamp) FROM {current_table}'''
    with sqlite3.connect(os.environ['DB_PATH']) as db:
        max_db_time = db.cursor().execute(max_ts_str)
        return max_db_time.fetchall()[0][0]

def get_latest_month_memedata(subreddit):
    global MONTH_TD
    global LAG_15MIN
    
    now= int(time.time() - LAG_15MIN)
    data_table = f'{subreddit}_scoring'
    select_latest_month = f"""
        Select *
        FROM {data_table}
        WHERE timestamp > {now-MONTH_TD}
    """
    with sqlite3.connect(os.environ['DB_PATH']) as db:
        return pd.read_sql(select_latest_month, db)

def insert_meme_data(current_table, cols):
    col_ord_str = str(cols)[1:-1].replace("'", "")
    return f''' INSERT INTO {current_table}({col_ord_str}) VALUES({','.join(['?']*len(cols))}) '''

def check_table_exists(current_table):
    return f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{current_table}';"""

def get_db_list():
    db_list = []
    with sqlite3.connect(os.environ['DB_PATH']) as db:
        for db_name in db.cursor().execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
            db_list.append(db_name[0])
    return db_list

def remove_duplicates(current_table):
    delete_dups_str = f"""
        DELETE FROM {current_table}
        WHERE rowid NOT IN (
            SELECT min(rowid)
            FROM {current_table}
            GROUP BY id
        ); 
    """

    print(delete_dups_str)
    with sqlite3.connect(os.environ['DB_PATH']) as db:
        db.cursor().execute(delete_dups_str)

def remove_dups_all_tables():
    db_list = get_db_list()
    for db_name in db_list:
        remove_duplicates(db_name)

def create_table(name, cols=''):
    if not cols:
        cols = """
            id TEXT UNIQUE,
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

    sql_create_table = f'CREATE TABLE IF NOT EXISTS {name}(' + cols + ');'

    with sqlite3.connect(os.environ['DB_PATH']) as db:
        db.cursor().execute(sql_create_table)
