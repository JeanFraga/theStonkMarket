from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from templates import build_template_db
from schema import DB


def build_db():
    DB.create_all()
    build_template_db()

if __name__=="__main__":
    build_db()