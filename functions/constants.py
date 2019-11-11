from os import environ
from multiprocessing import cpu_count

DEBUG_REDDIT = True
MONTH_TD = 60*60*24*30
DAY_TD = 60*60*24
FILE_TYPES = [".jpg", ".jpeg", ".png"]

NUM_WORKERS = cpu_count()

WORKER_DB_URI = environ['WORKER_DB_URI']
DB_PATH = environ['DB_PATH']
IMGDIR_PATH = environ['databases/imgdir']