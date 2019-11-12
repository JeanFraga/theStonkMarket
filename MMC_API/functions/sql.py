import sqlite3
import time
from datetime import datetime
import time
import pandas as pd
import os
from time import time, mktime
from MMC_API.functions.constants import MONTH_TD, DB_PATH

# SQL strings #####################################################################

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

select_from = """
        Select {}
        FROM {}
    """

# data loaders #####################################################################

def get_scoring_df(subreddit, cols):
    col_ord_str = str(cols)[1:-1].replace("'", "")
    table = f'{subreddit}_scoring'
    with sqlite3.connect(DB_PATH) as db:
        return pd.read_sql(select_from.format(col_ord_str, table), db)

# generate sql string ##################################################################### 

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
    return f''' SELECT {col_ord_str} FROM {table} WHERE {condition}'''

def check_table_exists(table):
    return f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"""

# get info #####################################################################

def get_max_timestamp(table):
    max_ts_str = f'''SELECT MAX(timestamp) FROM {table}'''
    with sqlite3.connect(DB_PATH) as db:
        max_db_time = db.cursor().execute(max_ts_str)
    return max_db_time.fetchall()[0][0]

def get_table_list():
    db_list = []
    with sqlite3.connect(DB_PATH) as db:
        for db_name in db.cursor().execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
            db_list.append(db_name[0])
    return db_list

def get_time_range(table, year, month, day=1, hour=0, minute=0):
    kwargs = {
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'minute': minute
    }
    fresh_month_ts = mktime(datetime(**kwargs).timetuple())

    max_db_time = get_max_timestamp(table)
    if not max_db_time: max_db_time = fresh_month_ts

    if month == 12:
        kwargs['month'] = 1
        kwargs['year'] += 1
    else: kwargs['month'] += 1

    next_month_ts = mktime(datetime(**kwargs).timetuple())

    return max_db_time, next_month_ts

# removers #####################################################################

def del_over_month_old(table):
    month_ago = int(time()) - MONTH_TD
    delete_over_month_old_str = f"""
        DELETE FROM {table}
        WHERE timestamp < {month_ago}; 
    """
    with sqlite3.connect(DB_PATH) as db:
        db.cursor().execute(delete_over_month_old_str)

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

# creators #####################################################################

def create_table(name, cols=''):
    if not cols:
        global memedata_schema
        cols = memedata_schema

    sql_create_table = f'CREATE TABLE IF NOT EXISTS {name}(' + cols + ');'

    with sqlite3.connect(DB_PATH) as db:
        db.cursor().execute(sql_create_table)

def table_prep(table, cols=''):
    with sqlite3.connect(DB_PATH) as db:
        exists = db.cursor().execute(check_table_exists(table)).fetchall()
    if not exists:
        create_table(table, cols=cols)
        return True
    return False
