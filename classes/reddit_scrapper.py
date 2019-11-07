from datetime import datetime
from tinydb import TinyDB
from multiprocessing import Manager, Pool, current_process
from tqdm import tqdm
from time import time

import pandas as pd
from numpy import log, e

from functions.pushshift import query_pushshift
from functions.praw import extract_data
from functions.misc import setup_logger, init_reddit
from functions.workerdb_compilers import insert_new_data, clear_worker_dbs
from functions.sql import (get_max_timestamp,
                            check_table_exists,
                            table_prep,
                            get_time_range,
                            get_scoring_df,
                            remove_duplicates,
                            del_over_month_old)
from functions.constants import (MONTH_TD,
                                WORKER_DB_URI,
                                FILE_TYPES,
                                NUM_WORKERS,
                                DAY_TD,
                                DEBUG_REDDIT)


import logging
reddit_bug_logger = setup_logger(__name__, 'logs/reddit_debug.log', level=logging.DEBUG)
info_logger = setup_logger(__name__, 'logs/INFO.log', level=logging.INFO)

# global functions for multiprocessing  #####################################################

def initializer():
    global worker_db
    global reddit

    worker_id = (int(current_process().name.split("-", 1)[1])-1) % NUM_WORKERS
    worker_db = TinyDB(WORKER_DB_URI.format(worker_id))

    while True:
        try:
            reddit = init_reddit(worker_id)
            break
        except Exception as e:
            if DEBUG_REDDIT: reddit_bug_logger.debug(e)
            worker_id = (worker_id + 1) % NUM_WORKERS

def praw_by_id(submission_id):
    try:
        submission = reddit.submission(id=submission_id)
        if not submission.stickied:
            data = extract_data(submission)
            if any(submission.url.endswith(filetype) for filetype in FILE_TYPES): worker_db.insert(data)
    except Exception as e:
        if DEBUG_REDDIT: reddit_bug_logger.debug(e)

class RedditScrapper:
    def __init__(self):
        self.scrapped = 0

# handle subreddits #####################################################

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

# engines #####################################################

    def engine(self, start_at, end_at):
        post_ids = query_pushshift(self.current_subreddit, start_at, end_at)
        with Pool(NUM_WORKERS, initializer) as workers:
            list(tqdm(workers.imap_unordered(praw_by_id, post_ids), total=len(post_ids)))
        self.scrapped += len(post_ids)

    def feed_engine_daily_chunks(self, table, current_ts, end_at, verbose=True):
        now = int(time())
        clear_worker_dbs()

        while current_ts < end_at:
            start_at = current_ts
            current_ts = min(start_at + DAY_TD, end_at, now)

            self.engine(start_at, current_ts)
            insert_new_data(table)
            clear_worker_dbs()

            info_logger.info(f'{self.scrapped} data points have been gathered in runtime so far.')
            if verbose: print(f'\n{self.scrapped} data points have been gathered in runtime so far.\n')
        remove_duplicates(table)

# scrapping #####################################################

    def scoringdb_update(self):
        table = f'{self.current_subreddit}_scoring'
        now = int(time())

        if table_prep(table):
            current_ts = now - MONTH_TD
            self.feed_engine_daily_chunks(table, current_ts, now)
        else:
            current_ts = get_max_timestamp(table)
            if not current_ts:
                current_ts = now - MONTH_TD
            self.feed_engine_daily_chunks(table, current_ts, now)
            del_over_month_old(table)

    def scrap_month(self, year, month, verbose=True):
        table = f'{self.current_subreddit}_{year}_{month}'

        table_prep(table)
        current_ts, next_month = get_time_range(table, year, month)

        self.feed_engine_daily_chunks(table, current_ts, next_month)
        if verbose: print(f'month {month} completed\n')

# loading #####################################################

    def get_scoring_data(self, update=True):
        if update: self.scoringdb_update()
        wanted_cols = ['day', 'author', 'upvotes', 'downvotes', 'upvote_ratio', 'num_comments']
        return get_scoring_df(self.current_subreddit, wanted_cols)

    def get_latest_scores(self):
        df = self.get_scoring_data()
        scoring = df[df['author']!='None']
        top_1percent = scoring[scoring['upvotes'] > scoring['upvotes'].quantile(0.99)]
        bottom_99percent = scoring[scoring['upvotes'] < scoring['upvotes'].quantile(0.99)]
        lowest_upvotes_in_top = top_1percent['upvotes'].min()

        num_memes_in_bottom = (bottom_99percent.groupby('author')
                                        .apply(len)
                                        .sort_values(ascending=False))
        num_memes_in_top = (top_1percent.groupby('author')
                                        .apply(len)
                                        .sort_values(ascending=False))
        highest_upvotes = top_1percent.groupby('author')['upvotes'].max()

        scores_dict = {}
        for author in list(top_1percent['author']):
            try:
                part1 = (num_memes_in_top[author]**1.5/num_memes_in_bottom[author])
            except:
                part1 = 2.2*num_memes_in_top[author]**1.5
            part2 = log(e+(highest_upvotes[author]/lowest_upvotes_in_top))
            scores_dict[author] = part1 * part2

        return pd.DataFrame.from_dict(scores_dict, orient='index').iloc[:,0].sort_values(ascending=False)
