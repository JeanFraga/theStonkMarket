import math
import numpy as np
import pandas as pd

import os
import io
import json
import time
import requests
import sqlite3
import pprint as pp

import tqdm
import praw
import multiprocessing

from datetime import datetime, timedelta
from tinydb import TinyDB

from custom_functions.timeit import timeit
from custom_functions.pushshift import query_pushshift
from custom_functions.sql import create_meme_table
from custom_functions.sql import insert_meme_sql_string

db_uri = r'db_{}.json'
FILE_TYPES = [".jpg", ".jpeg", ".png"]


def compile_data(current_table):
    columns = ['id', 'title', 'author', 'timestamp', 'media', 'meme_text', 'filename', 'datetime', 'year',
               'month', 'day', 'hour', 'minute', 'upvote_ratio', 'upvotes', 'downvotes', 'nsfw', 'num_comments']
    cdf = pd.DataFrame(columns=columns)
    for i in range(0, 8):
        with open(db_uri.format(i), "r") as data:
            json_data = json.load(data)
        os.remove(db_uri.format(i))

        df = pd.DataFrame.from_dict(json_data['_default']).transpose()
        cdf = pd.concat([cdf, df], ignore_index=True, axis=0, sort=True)

    with sqlite3.connect("memes.db") as db:
        data = list(cdf.iloc[:, ::-1].itertuples(index=False, name=None))
        db.cursor().executemany(insert_meme_sql_string.format(current_table), data)


# get post contents via PRAW from post id
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
                    "filename": None,
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

            except Exception as e:
                print(e)

    except:
        pass


def initializer():

    global db
    global reddit
    global db_uri

    worker = (
        int(multiprocessing.current_process().name.split("-", 1)[1])-1) % 8
    db = TinyDB(db_uri.format(worker))
    if worker in [1, 3, 4, 6, 7]:
        worker = 0

    reddit_oauth = json.loads(os.environ['reddit_oauth_'+str(worker)])
    reddit = praw.Reddit(client_id=reddit_oauth['CLIENT_ID'],
                         client_secret=reddit_oauth['CLIENT_SECRET'],
                         password=reddit_oauth['PASSWORD'],
                         user_agent=reddit_oauth['USERAGENT'],
                         username=reddit_oauth['USERNAME'])


# multiprocess praw over ids
def praw_post_ids(post_ids):

    NUM_WORKERS = 8
    p = multiprocessing.Pool(NUM_WORKERS, initializer)

    # tqdm displays progress bar for multiprocessing
    list(tqdm.tqdm(p.imap_unordered(praw_by_id, post_ids), total=len(post_ids)))
    p.close()
    p.join()


def main():
    current = 0
    step_size = 60*60*24
    year = 2019
    subreddit = 'dankmemes'

    for i in range(1, 13):
        table = f'{subreddit}_{year}_{i}'
        check_table_exists = f"""SELECT name FROM sqlite_master WHERE type='table' AND name='table';"""
        with sqlite3.connect("memes.db") as db:
            exists = db.cursor().execute(check_table_exists).fetchall()
        if not exists:
            create_meme_table(table)

    for i in range(1, 13):
        current_table = f'{subreddit}_{year}_{i}'
        dt = datetime(year=year, month=i, day=1, hour=0, minute=0)
        fresh_month_ts = time.mktime(dt.timetuple())

        select_max_timestamp = f'''SELECT MAX(timestamp) FROM {current_table}'''
        with sqlite3.connect("memes.db") as db:
            max_timestamp = db.cursor().execute(
                select_max_timestamp).fetchall()[0][0]
        if not max_timestamp:
            max_timestamp = fresh_month_ts

        if i == 12:
            next_month = 1
            year += 1
        else:
            next_month = i+1

        dt = datetime(year=year, month=next_month, day=1, hour=0, minute=0)
        next_month_ts = time.mktime(dt.timetuple())

        while current < next_month_ts:
            start_at = int(max_timestamp)
            end_at = int(min(max_timestamp + step_size, time.time()))

            current = end_at
            post_ids = query_pushshift(subreddit, start_at, end_at)
            praw_post_ids(post_ids)
            compile_data(current_table)


if __name__ == "__main__":
    main()
