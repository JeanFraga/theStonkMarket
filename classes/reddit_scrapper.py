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
from functions.sql import (create_meme_table,
                            get_max_timestamp,
                            check_table_exists,
                            table_prep,
                            set_time_range)
from functions.pushshift import query_pushshift


worker_db_uri = r'worker_dbs/db_{}.json'
FILE_TYPES = [".jpg", ".jpeg", ".png"]
num_workers = 8

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

    global worker_db_uri
    global db
    global reddit
    global num_workers

    raw_id = multiprocessing.current_process().name.split("-", 1)[1]
    worker_id = (int(raw_id)-1) % num_workers

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
        except: worker_id = (worker_id + 1) % num_workers

class RedditScrapper:
    def __init__(self, step_size = 60*60*24):
        self.step_size = step_size
        self.scrapped = 0

    def scrap_month(self, subreddit, year, month):
        current_table = table_prep(subreddit, year, month)
        max_db_time, next_month = set_time_range(current_table, year, month)

        while max_db_time < next_month:
            start_at = int(max_db_time)
            end_at = int(min(max_db_time + self.step_size, time.time()))

            self.scrapper_engine(subreddit, start_at, end_at)
            insert_new_data(current_table)


    def scrapper_engine(self, subreddit, start_at, end_at):
        def praw_post_ids(post_ids):
            global num_workers
            p = multiprocessing.Pool(num_workers, initializer)
            list(tqdm.tqdm(p.imap_unordered(praw_by_id, post_ids), total=len(post_ids)))
            p.close()
            p.join()

        post_ids = query_pushshift(subreddit, start_at, end_at)
        praw_post_ids(post_ids)