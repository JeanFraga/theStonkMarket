import sqlite3


def insert_meme_sql_string(current_table, names_list):
    col_ord_str = str(names_list)[1:-1].replace("'", "")
    return f''' INSERT INTO {current_table}({col_ord_str}) VALUES({','.join(['?']*len(names_list))}) '''


def create_meme_table(name):
    cols = """(
        id TEXT,
        title TEXT,
        author TEXT,
        media TEXT,
        meme_text TEXT,
        status TEXT,
        timestamp INTEGER,
        datetime DATETIME,
        year INTEGER,
        month INTEGER,
        day INTEGER,
        hour INTEGER,
        minute INTEGER,
        upvote_ratio FLOAT,
        upvotes INTEGER,
        downvotes INTEGER,
        nsfw BOOL,
        num_comments INTEGER
    );"""

    sql_create_table = f'CREATE TABLE IF NOT EXISTS {name}' + cols

    with sqlite3.connect("memes.db") as db:
        db.cursor().execute(sql_create_table)
