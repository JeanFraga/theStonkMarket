DATASET_PATH = 'Stonks/databases/dataset'

from os import environ
from multiprocessing import cpu_count

DEBUG_REDDIT = True
MONTH_TD = 60*60*24*30
DAY_TD = 60*60*24
FILE_TYPES = [".jpg", ".jpeg", ".png"]
NUM_WORKERS = cpu_count()