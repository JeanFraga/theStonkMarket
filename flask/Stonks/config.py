from decouple import config
class BaseConfig(object):

    if config('FLASK_ENV') == 'development':
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        DEBUG = True
        SQLALCHEMY_DATABASE_URI='sqlite:///databases/db.sqlite3'

    else:
        SECRET_KEY = config('SECRET_KEY')
        DEBUG = config('DEBUG')
        DB_NAME = config('DB_NAME')
        DB_USER = config('DB_USER')
        DB_PASS = config('DB_PASS')
        DB_SERVICE = config('DB_SERVICE')
        DB_PORT = config('DB_PORT')
        SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
            DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
        )
