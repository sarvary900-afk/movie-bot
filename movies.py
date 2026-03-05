from database import sql, db
import random

def add_movie(code,name,genre,file_id):

    sql.execute(
    "INSERT INTO movies VALUES (?,?,?,?,?,?)",
    (code,name,genre,file_id,0,0)
    )

    db.commit()


def get_movie(code):

    sql.execute("SELECT * FROM movies WHERE code=?", (code,))
    return sql.fetchone()


def search_movie(text):

    sql.execute(
    "SELECT code,name FROM movies WHERE name LIKE ?",
    ('%'+text+'%',)
    )

    return sql.fetchall()


def random_movie():

    sql.execute("SELECT * FROM movies ORDER BY RANDOM() LIMIT 1")
    return sql.fetchone()


def top_movies():

    sql.execute("SELECT name,views FROM movies ORDER BY views DESC LIMIT 10")
    return sql.fetchall()


def new_movies():

    sql.execute("SELECT code,name FROM movies ORDER BY rowid DESC LIMIT 10")
    return sql.fetchall()
