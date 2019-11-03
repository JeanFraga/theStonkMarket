import sqlite3
import time
from datetime import datetime

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

def table_prep(subreddit, year, month):
    current_table = f'{subreddit}_{year}_{month}'

    with sqlite3.connect("memes.db") as db:
        exists = db.cursor().execute(check_table_exists(current_table)).fetchall()
    if not exists:
        create_meme_table(current_table)
    
    return current_table

def get_max_timestamp(current_table):
    max_ts_str = f'''SELECT MAX(timestamp) FROM {current_table}'''
    with sqlite3.connect("memes.db") as db:
        max_db_time = db.cursor().execute(max_ts_str)
        return max_db_time.fetchall()[0][0]


def insert_meme_sql_string(current_table, names_list):
    col_ord_str = str(names_list)[1:-1].replace("'", "")
    return f''' INSERT INTO {current_table}({col_ord_str}) VALUES({','.join(['?']*len(names_list))}) '''

def check_table_exists(current_table):
    return f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{current_table}';"""

def create_meme_table(name):
    cols = """(
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
    );"""

    sql_create_table = f'CREATE TABLE IF NOT EXISTS {name}' + cols

    with sqlite3.connect("memes.db") as db:
        db.cursor().execute(sql_create_table)
