
from Stonks.scripts.templates import build_template_db
from Stonks.schema import DB


def build_db():
    DB.create_all()
    build_template_db()

if __name__=="__main__":
    build_db()