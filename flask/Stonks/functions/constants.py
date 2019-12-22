from multiprocessing import cpu_count

DATASET_PATH = 'Stonks/databases/dataset'
DEBUG_REDDIT = True
MONTH_TD = 60*60*24*30
DAY_TD = 60*60*24
FILE_TYPES = [".jpg", ".jpeg", ".png"]
NUM_WORKERS = cpu_count()
IN_DEV = config('FLASK_ENV') == 'devolpment'
REDDIT_LOG_PATH = 'Stonks/logs/reddit_debug.log' if IN_DEV else 'reddit_debug.log'
INFO_LOG_PATH = 'Stonks/logs/INFO.log' if IN_DEV else 'INFO.log'