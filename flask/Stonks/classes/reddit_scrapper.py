from datetime import datetime
from multiprocessing import Pool, current_process
from tqdm import tqdm
from time import time
import pandas as pd
import matplotlib.pyplot as plt
import json, logging

from Stonks.schema import Current_Month, DB

from Stonks.functions.dataframe import score_df, save_table_img
from Stonks.functions.pushshift import query_pushshift
from Stonks.functions.praw import extract_data
from Stonks.functions.misc import setup_logger, init_reddit, check_isDeleted
from Stonks.functions.constants import (
    MONTH_TD,
    FILE_TYPES,
    NUM_WORKERS,
    DAY_TD,
    DEBUG_REDDIT,
    REDDIT_LOG_PATH,
    INFO_LOG_PATH
)

reddit_bug_logger = setup_logger(__name__, REDDIT_LOG_PATH, level=logging.DEBUG)
info_logger = setup_logger(__name__, INFO_LOG_PATH, level=logging.INFO)

def initializer():
    global reddit
    worker_id = (int(current_process().name.split("-", 1)[1])-1) % NUM_WORKERS

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
            if any(submission.url.endswith(filetype) for filetype in FILE_TYPES):
                return extract_data(submission)
    except Exception as e:
        if DEBUG_REDDIT: reddit_bug_logger.debug(e)

class RedditScrapper:
    def __init__(self, subreddit, verbose=True):
        self.current_subreddit = subreddit
        self.verbose = verbose

    def engine(self, start_time, end_time):
        post_ids = query_pushshift(self.current_subreddit, start_time, end_time)
        with Pool(NUM_WORKERS, initializer) as workers:
            data_list = list(tqdm(workers.imap_unordered(praw_by_id, post_ids), total=len(post_ids)))

        DB.session.add_all([Current_Month(**data) for data in data_list if data])
        DB.session.commit()

        info_logger.info(f'{len(data_list)} data points have been gathered in runtime so far.')
        if self.verbose: print(f'\n{len(data_list)} data points have been gathered in runtime so far.\n')


    def feed_engine_daily_chunks(self, current_ts, end_time):
        now = int(time())

        while current_ts < end_time:
            start_time = current_ts
            current_ts = min(start_time + DAY_TD, end_time, now)

            self.engine(start_time, current_ts)

    def update_current_month(self):
        now = int(time())
        current_ts = DB.session.query(DB.func.max(Current_Month.timestamp)).scalar()

        if not current_ts:
            current_ts = now - MONTH_TD

        self.feed_engine_daily_chunks(current_ts, now)

        DB.session.query(Current_Month.timestamp < (now - MONTH_TD)).delete()

    def get_score_df(self, top=None):
        self.update_current_month()
        df = score_df(pd.read_sql(
            DB.session.query(Current_Month).statement,
            DB.session.bind)
        ).iloc[:5, :].drop(columns=['timestamp'])

        save_table_img(df)

        return json.loads(df.to_json(orient='table', index=False))["data"]