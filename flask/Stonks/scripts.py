from Stonks.schema import DB
from Stonks.scripts.templatedb_builder.py import build_template_db

def on_app_init():
    DB.create_all()
    build_template_db()