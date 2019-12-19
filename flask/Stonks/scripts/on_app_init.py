from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from flask import current_app

from templates import build_template_db
from schema import DB


def build_db():
    DB.create_all()
    build_template_db()

if __name__=="__main__":
    with current_app.app_context():
        build_db()