from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from flask import current_app as app

from templates import build_template_db
from schema import DB
from app import create_app


def build_db():
    DB.create_all()
    build_template_db()

if __name__=="__main__":
    app = create_app()
    with app.app_context():
        build_db()