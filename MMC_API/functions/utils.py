import logging
from praw import Reddit
from json import loads
from os import environ
from cv2 import cv2
import numpy as np

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(process)d:%(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def init_reddit(id):
    env_var_key = 'reddit_oauth_'+str(id)
    reddit_oauth = loads(environ[env_var_key])
    return Reddit(client_id=reddit_oauth['CLIENT_ID'],
                    client_secret=reddit_oauth['CLIENT_SECRET'],
                    password=reddit_oauth['PASSWORD'],
                    user_agent=reddit_oauth['USERAGENT'],
                    username=reddit_oauth['USERNAME'])

def check_isDeleted(output_filename):
    deleted = cv2.imread('static/deleted_img/image404.png')
    deleted_nb = cv2.imread('static/deleted_img/image404_nb.png')
    image = cv2.imread(output_filename)

    try:
        diff = cv2.subtract(image, deleted)
    except:
        diff = True
    try:
        diff_nb = cv2.subtract(image, deleted_nb)
    except:
        diff_nb = True

    return (np.all(diff == 0) | np.all(diff_nb == 0))