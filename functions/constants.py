import os

MONTH_TD = 60*60*24*30
LAG_15MIN = 60*15
WORKER_DB_URI = r'worker_dbs/db_{}.json'
FILE_TYPES = [".jpg", ".jpeg", ".png"]
NUM_WORKERS = os.environ['NUM_WORKERS']