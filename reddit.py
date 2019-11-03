from datetime import datetime, timedelta
from tinydb import TinyDB
import multiprocessing
from praw import Reddit
import tqdm
import sqlite3
import requests
import time
import json
import io
import os
import pandas as pd
import numpy as np
import math
from functions.workerdb_compilers import insert_new_data
from functions.sql import create_meme_table, get_max_timestamp
from functions.pushshift import query_pushshift
import os
import sys


worker_db_uri = r'worker_dbs/db_{}.json'
FILE_TYPES = [".jpg", ".jpeg", ".png"]
total = 0

subreddits = ['dankmemes']
years = [2019]
step_size = 60*60*24
NUM_WORKERS = 8


def praw_by_id(submission_id):
    try:
        submission = reddit.submission(id=submission_id)
        if submission.stickied:
            pass
        else:
            try:
                data = {
                    "id": submission.id,
                    "title": submission.title,
                    "author": str(submission.author),
                    "timestamp": submission.created_utc,
                    "status": None,
                    "datetime": datetime.fromtimestamp(submission.created_utc).isoformat(),
                    "year": datetime.fromtimestamp(submission.created_utc).year,
                    "month": datetime.fromtimestamp(submission.created_utc).month,
                    "day": datetime.fromtimestamp(submission.created_utc).day,
                    "hour": datetime.fromtimestamp(submission.created_utc).hour,
                    "minute": datetime.fromtimestamp(submission.created_utc).minute,
                    "media": submission.url,
                    "upvote_ratio": submission.upvote_ratio,
                    "upvotes": submission.score,
                    "downvotes": round(submission.score / submission.upvote_ratio) - submission.score,
                    "nsfw": submission.over_18,
                    "num_comments": submission.num_comments
                }

                if any(submission.url.endswith(filetype) for filetype in FILE_TYPES):
                    db.insert(data)

            except:
                pass

    except:
        pass


def initializer():

    global worker_db_uri
    global db
    global reddit
    global NUM_WORKERS

    raw_id = multiprocessing.current_process().name.split("-", 1)[1]
    worker_id = (int(raw_id)-1) % NUM_WORKERS

    db = TinyDB(worker_db_uri.format(worker_id))

    while True:
        try:
            env_var_key = 'reddit_oauth_'+str(worker_id)
            reddit_oauth = json.loads(os.environ[env_var_key])
            reddit = Reddit(client_id=reddit_oauth['CLIENT_ID'],
                                 client_secret=reddit_oauth['CLIENT_SECRET'],
                                 password=reddit_oauth['PASSWORD'],
                                 user_agent=reddit_oauth['USERAGENT'],
                                 username=reddit_oauth['USERNAME'])
            break
        except:
            print(worker_id)
            worker_id = (worker_id + 1) % NUM_WORKERS


def praw_post_ids(post_ids):

    global NUM_WORKERS
    p = multiprocessing.Pool(NUM_WORKERS, initializer)
    list(tqdm.tqdm(p.imap_unordered(praw_by_id, post_ids), total=len(post_ids)))
    p.close()
    p.join()


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


def scrapper_engine(subreddit, max_db_time, next_month, current_table):
    global step_size
    global total

    while max_db_time < next_month:
        start_at = int(max_db_time)
        end_at = int(min(max_db_time + step_size, time.time()))

        post_ids = query_pushshift(subreddit, start_at, end_at)
        praw_post_ids(post_ids)
        insert_new_data(current_table)

        max_db_time = end_at
        total += len(post_ids)
        print(f'\n{total} data points have been compiled so far in runtime.\n')


def main():
    global years
    global subreddits
    for subreddit in subreddits:
        for year in years:
            for month in range(1, 13):

                current_table = f'{subreddit}_{year}_{month}'
                check_table_exists = f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{current_table}';"""

                with sqlite3.connect("memes.db") as db:
                    exists = db.cursor().execute(check_table_exists).fetchall()
                if not exists:
                    create_meme_table(current_table)

                max_db_time, next_month = set_time_range(
                    current_table, year, month)
                scrapper_engine(subreddit, max_db_time,
                                next_month, current_table)


if __name__ == "__main__":
    main()
