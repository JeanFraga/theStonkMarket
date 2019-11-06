from datetime import datetime
from tinydb import TinyDB
from multiprocessing import Manager, Pool, current_process
from praw import Reddit
from tqdm import tqdm
from time import time, sleep
from json import loads
from os import environ
from functions.pushshift import query_pushshift
from functions.praw import extract_data
from functions.workerdb_compilers import insert_new_data, clear_worker_dbs
from functions.sql import (get_max_timestamp,
                            check_table_exists,
                            table_prep,
                            set_time_range,
                            get_scoring_df,
                            remove_duplicates)
from functions.constants import (MONTH_TD,
                                LAG_15MIN,
                                WORKER_DB_URI,
                                FILE_TYPES,
                                NUM_WORKERS,
                                MAX_RETRIES)

import logging
format = '%(asctime)s:%(levelname)s:%(message)s'
logging.basicConfig(filename='test.log', level=logging.DEBUG, format=format)

def initializer():
    global worker_db
    global reddit

    worker_id = (int(current_process().name.split("-", 1)[1])-1) % NUM_WORKERS
    worker_db = TinyDB(WORKER_DB_URI.format(worker_id))

    while True:
        try:
            env_var_key = 'reddit_oauth_'+str(worker_id)
            reddit_oauth = loads(environ[env_var_key])
            reddit = Reddit(client_id=reddit_oauth['CLIENT_ID'],
                                client_secret=reddit_oauth['CLIENT_SECRET'],
                                password=reddit_oauth['PASSWORD'],
                                user_agent=reddit_oauth['USERAGENT'],
                                username=reddit_oauth['USERNAME'])
            break
        except Exception as e:
            logging.debug(e)
            worker_id = (worker_id + 1) % NUM_WORKERS

def praw_by_id(submission_id):
    try:
        submission = reddit.submission(id=submission_id)
        if not submission.stickied:
            data = extract_data(submission)
            if any(submission.url.endswith(filetype) for filetype in FILE_TYPES): worker_db.insert(data)
    except Exception as e:
        logging.debug(e)

class RedditScrapper:
    def __init__(self):
        self.scrapped = 0

################# handle subreddits #####################################

    def set_current_subreddit(self, subreddit):
        self.current_subreddit = subreddit

    def _subreddit_list_iterator(self):
        for subreddit in self.subreddit_list: yield subreddit

    def set_subreddit_list(self, subreddit_list):
        self.subreddit_list = subreddit_list
        self.subreddit_generator = self._subreddit_list_iterator()
        self.current_subreddit = next(self.subreddit_generator)

    def next_subreddit(self):
        self.current_subreddit = next(self.subreddit_generator)

################# engines #####################################

    def engine(self, start_at, end_at):
        post_ids = query_pushshift(self.current_subreddit, start_at, end_at)
        with Pool(NUM_WORKERS, initializer) as workers:
            list(tqdm(workers.imap_unordered(praw_by_id, post_ids), total=len(post_ids)))
        self.scrapped += len(post_ids)

    def feed_engine_td_chunks(self, table, current_ts, end_at, stepsize_td=60*60*24):
        now = int(time()) - LAG_15MIN
        clear_worker_dbs()

        while current_ts < end_at:
            start_at = current_ts
            current_ts = min(start_at + stepsize_td, end_at, now)

            self.engine(start_at, current_ts)
            insert_new_data(table)
            clear_worker_dbs()

            print(f'\n{self.scrapped} data points have been gathered in runtime so far.\n')
        remove_duplicates(table)

################# scrapping #####################################

    def scoringdb_update(self):
        table = f'{self.current_subreddit}_scoring'
        now = int(time()) - LAG_15MIN

        if table_prep(table):
            current_ts = now - MONTH_TD
            self.feed_engine_td_chunks(table, current_ts, now)
        else:
            current_ts = get_max_timestamp(table)
            if not current_ts:
                current_ts = now - MONTH_TD
            self.feed_engine_td_chunks(table, current_ts, now)

    def scrap_month(self, year, month):
        table = f'{self.current_subreddit}_{year}_{month}'

        table_prep(table)
        current_ts, next_month = set_time_range(table, year, month)

        self.feed_engine_td_chunks(table, current_ts, next_month)
        print(f'month {month} completed\n')

################# loading #####################################

    def load_scoring_data(self):
        return get_scoring_df(self.current_subreddit)
