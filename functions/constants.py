import os

DEBUG_REDDIT = True
MONTH_TD = 60*60*24*30
DAY_TD = 60*60*24
WORKER_DB_URI = r'databases/worker_dbs/db_{}.json'
FILE_TYPES = [".jpg", ".jpeg", ".png"]
NUM_WORKERS = int(os.environ['NUM_WORKERS'])
DB_PATH = os.environ['DB_PATH']