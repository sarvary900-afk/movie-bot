from config import CHANNELS
from database import sql, db

def add_user(user, ref):

    sql.execute("SELECT user_id FROM users WHERE user_id=?", (user,))
    if not sql.fetchone():

        sql.execute("INSERT INTO users VALUES (?,?)", (user, ref))
        db.commit()


def get_users():

    sql.execute("SELECT user_id FROM users")
    return sql.fetchall()
