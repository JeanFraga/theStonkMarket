from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from templates import build_template_db
from schema import DB
from config import BaseConfig

from flask import Flask

def build_db():
    DB.create_all()
    build_template_db()

if __name__=="__main__":
    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    with app.app_context():
        DB.init_app(app)
        build_db()