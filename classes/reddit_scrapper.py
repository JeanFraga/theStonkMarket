from datetime import datetime
from tinydb import TinyDB
import multiprocessing
from praw import Reddit
import tqdm
import sqlite3
import time
import json
import io
import os
import pandas as pd
import numpy as np
from functions.workerdb_compilers import insert_new_data, clear_worker_dbs
from functions.sql import (get_max_timestamp,
                            check_table_exists,
                            table_prep,
                            set_time_range,
                            get_latest_month_memedata)
from functions.pushshift import query_pushshift
from functions.constants import *

def praw_by_id(submission_id):
        try:
            submission = reddit.submission(id=submission_id)
            if submission.stickied: pass
            else:
                try:
                    data = {
                        "id": submission.id,
                        "title": submission.title,
                        "author": str(submission.author),
                        "timestamp": submission.created_utc,
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

                    if any(submission.url.endswith(filetype) for filetype in FILE_TYPES): db.insert(data)

                except: pass
        except: pass

def initializer():

    global WORKER_DB_URI
    global db
    global reddit
    global NUM_WORKERS

    raw_id = multiprocessing.current_process().name.split("-", 1)[1]
    worker_id = (int(raw_id)-1) % NUM_WORKERS

    db = TinyDB(WORKER_DB_URI.format(worker_id))

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
        except: worker_id = (worker_id + 1) % NUM_WORKERS

class RedditScrapper:
    def __init__(self, step_size = 60*60):
        self.step_size = step_size
        self.scrapped = 0

    def scrapper_engine(self, subreddit, start_at, end_at):
        def praw_post_ids(post_ids):
            global NUM_WORKERS
            p = multiprocessing.Pool(NUM_WORKERS, initializer)
            list(tqdm.tqdm(p.imap_unordered(praw_by_id, post_ids), total=len(post_ids)))
            p.close()
            p.join()

            self.scrapped += len(post_ids)

        clear_worker_dbs()
        post_ids = query_pushshift(subreddit, start_at, end_at)
        praw_post_ids(post_ids)

    def feed_engine_td_chunks(self, subreddit, data_table, current_ts, end_at, stepsize_td=60*60*24):
        now = int(time.time()) - LAG_15MIN
        while current_ts < end_at:
            start_at = current_ts
            current_ts = min(start_at + stepsize_td, end_at, now)

            self.scrapper_engine(subreddit, start_at, current_ts)
            insert_new_data(data_table)

            print(f'\n{self.scrapped} data points have been gathered in runtime so far.\n')

    def load_scoring_data(self, subreddit):
        return get_latest_month_memedata(subreddit)

    def scoringdb_update(self, subreddit):
        global MONTH_TD
        data_table = f'{subreddit}_scoring'

        if table_prep(data_table):
            now = int(time.time()) - LAG_15MIN
            current_ts = now - MONTH_TD

            self.feed_engine_td_chunks(subreddit, data_table, current_ts, now)
        else:
            now = int(time.time()) - LAG_15MIN
            current_ts = get_max_timestamp(data_table)
            if not current_ts:
                current_ts = now - MONTH_TD

            self.feed_engine_td_chunks(subreddit, data_table, current_ts, now)

    def scrap_month(self, subreddit, year, month):
        global MONTH_TD
        data_table = f'{subreddit}_{year}_{month}'

        table_prep(data_table)
        current_ts, next_month = set_time_range(data_table, year, month)

        self.feed_engine_td_chunks(subreddit, data_table, current_ts, next_month)
        print(f'month {month} completed\n')
