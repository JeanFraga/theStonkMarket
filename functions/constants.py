from os import environ
from multiprocessing import cpu_count

DEBUG_REDDIT = True
MONTH_TD = 60*60*24*30
DAY_TD = 60*60*24
WORKER_DB_URI = environ['WORKER_DB_URI']
FILE_TYPES = [".jpg", ".jpeg", ".png"]
NUM_WORKERS = cpu_count()
DB_PATH = environ['DB_PATH']
IMGDIR_PATH = 'databases/imgdir'