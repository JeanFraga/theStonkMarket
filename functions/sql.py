import sqlite3
from sqlite3 import Error


insert_meme_sql_string = ''' INSERT INTO {}(year, upvotes, upvote_ratio, title, timestamp, num_comments, nsfw, month, minute, meme_text, media, id, hour, status, downvotes, day, datetime, author) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''


def create_meme_table(name):
    sql_create_table = f""" CREATE TABLE IF NOT EXISTS {name} (
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
                                                            ); """

    with sqlite3.connect("memes.db") as db:
        db.cursor().execute(sql_create_table)
