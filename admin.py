from config import ADMIN_ID
from database import sql
from users import get_users

def is_admin(user):

    return user == ADMIN_ID


def user_count():

    sql.execute("SELECT COUNT(*) FROM users")
    return sql.fetchone()[0]
