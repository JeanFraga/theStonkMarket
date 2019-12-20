# from os import sys, path
# sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# from flask import current_app with current_app.app_context():

from Stonks.scripts.templates import build_template_db
from Stonks.schema import DB


def build_db():
    DB.drop_all()
    DB.create_all()
    return build_template_db()