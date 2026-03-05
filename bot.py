import telebot
import sqlite3
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN, ADMIN_ID, CHANNELS, POST_CHANNEL

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("kino.db", check_same_thread=False)
sql = db.cursor()

# ================= DATABASE =================

sql.execute("""CREATE TABLE IF NOT EXISTS movies(
code TEXT,
name TEXT,
genre TEXT,
year TEXT,
description TEXT,
file_id TEXT,
views INTEGER,
rating INTEGER,
premium INTEGER
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS users(
user_id INTEGER,
ref INTEGER
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS favorites(
user_id INTEGER,
code TEXT
)""")

db.commit()

waiting_movie = {}

MOVIES_PER_PAGE = 10

# ================= SUBSCRIBE CHECK =================

def check_sub(user_id):

    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status not in ["member","administrator","creator"]:
                return False
        except:
            return False
    return True

# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):

    user = message.from_user.id
    ref = None

    try:
        ref = int(message.text.split()[1])
    except:
        pass

    sql.execute("SELECT user_id FROM users WHERE user_id=?", (user,))
    if not sql.fetchone():
        sql.execute("INSERT INTO users VALUES (?,?)", (user,ref))
        db.commit()

    if not check_sub(user):

        text="❗ Kanallarga obuna bo‘ling\n\n"

        for ch in CHANNELS:
            text+=f"{ch}\n"

        bot.send_message(message.chat.id,text)
        return

    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📜 Kino Mundarijasi",callback_data="list"),
        InlineKeyboardButton("🔥 TOP",callback_data="top")
    )
    keyboard.row(
        InlineKeyboardButton("🎲 Random Kino",callback_data="random"),
        InlineKeyboardButton("🆕 Yangi Kinolar",callback_data="new")
    )

    bot.send_message(message.chat.id,"🎬 Kino kodini yuboring",reply_markup=keyboard)

# ================= ADMIN KINO QO'SHISH =================

@bot.message_handler(func=lambda m: m.text.startswith("/"))
def add_movie(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        text = message.text[1:]
        code,name = text.split(" ",1)

        waiting_movie[message.from_user.id] = (code,name,"Drama","2025","Yangi kino",0,0)

        bot.send_message(message.chat.id,"🎬 Endi kino videosini yuboring")

    except:

        bot.send_message(message.chat.id,"❌ Format:\n/256 Kino nomi")

# ================= VIDEO QABUL =================

@bot.message_handler(content_types=['video'])
def save_movie(message):

    if message.from_user.id in waiting_movie:

        code,name,genre,year,desc,rating,premium = waiting_movie[message.from_user.id]

        file_id = message.video.file_id

        sql.execute(
        "INSERT INTO movies VALUES (?,?,?,?,?,?,?,?,?)",
        (code,name,genre,year,desc,file_id,0,rating,premium)
        )

        db.commit()

        del waiting_movie[message.from_user.id]

        # Kanalga post qilish
        caption=f"""
🎬 {name}

📅 Yil: {year}
🎭 Janr: {genre}

📥 Ko‘rish uchun botga kiring
🤖 @{bot.get_me().username}

🔎 Kino kodi: {code}
"""

        bot.send_video(
        POST_CHANNEL,
        file_id,
        caption=caption
        )

        bot.send_message(message.chat.id,"✅ Kino saqlandi va kanalga joylandi")

# ================= MUNDARIJA =================

@bot.callback_query_handler(func=lambda c: c.data=="list")
def list_movies(call):

    show_page(call.message.chat.id,1)

def show_page(chat_id,page):

    offset=(page-1)*MOVIES_PER_PAGE

    sql.execute(
    "SELECT code,name FROM movies LIMIT ? OFFSET ?",
    (MOVIES_PER_PAGE,offset)
    )

    movies=sql.fetchall()

    text=f"🎬 Kino Mundarijasi ({page}-bet)\n\n"

    for m in movies:
        text+=f"{m[0]} — {m[1]}\n"

    keyboard=InlineKeyboardMarkup()

    keyboard.row(
    InlineKeyboardButton("⬅️",callback_data=f"page_{page-1}"),
    InlineKeyboardButton(str(page),callback_data="none"),
    InlineKeyboardButton("➡️",callback_data=f"page_{page+1}")
    )

    bot.send_message(chat_id,text,reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def page_callback(call):

    page=int(call.data.split("_")[1])

    if page<1:
        return

    show_page(call.message.chat.id,page)

# ================= TOP =================

@bot.callback_query_handler(func=lambda c: c.data=="top")
def top_movies(call):

    sql.execute("SELECT name,views FROM movies ORDER BY views DESC LIMIT 10")

    movies=sql.fetchall()

    text="🏆 TOP Kinolar\n\n"

    for i,m in enumerate(movies,1):
        text+=f"{i}. {m[0]} — {m[1]} ko‘rish\n"

    bot.send_message(call.message.chat.id,text)

# ================= RANDOM =================

@bot.callback_query_handler(func=lambda c: c.data=="random")
def random_movie(call):

    sql.execute("SELECT * FROM movies")

    movies=sql.fetchall()

    if movies:

        movie=random.choice(movies)

        bot.send_video(
        call.message.chat.id,
        movie[5],
        caption=f"🎬 {movie[1]}",
        protect_content=True
        )

# ================= YANGI KINO =================

@bot.callback_query_handler(func=lambda c: c.data=="new")
def new_movies(call):

    sql.execute("SELECT code,name FROM movies ORDER BY rowid DESC LIMIT 10")

    movies=sql.fetchall()

    text="🆕 Yangi Kinolar\n\n"

    for m in movies:
        text+=f"{m[0]} — {m[1]}\n"

    bot.send_message(call.message.chat.id,text)

# ================= STATS =================

@bot.message_handler(commands=['stats'])
def stats(message):

    if message.from_user.id != ADMIN_ID:
        return

    sql.execute("SELECT COUNT(*) FROM users")
    users=sql.fetchone()[0]

    sql.execute("SELECT COUNT(*) FROM movies")
    movies=sql.fetchone()[0]

    bot.send_message(message.chat.id,f"""
📊 Statistika

👤 Userlar: {users}
🎬 Kinolar: {movies}
""")

# ================= DELETE =================

@bot.message_handler(commands=['del'])
def delete_movie(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        code=message.text.split()[1]

        sql.execute("DELETE FROM movies WHERE code=?",(code,))
        db.commit()

        bot.send_message(message.chat.id,"🗑 Kino o‘chirildi")

    except:

        bot.send_message(message.chat.id,"❌ /del 123")

# ================= BROADCAST =================

@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/broadcast ","")

    sql.execute("SELECT user_id FROM users")
    users = sql.fetchall()

    for u in users:
        try:
            bot.send_message(u[0], text)
        except:
            pass

    bot.send_message(message.chat.id,"✅ Reklama yuborildi")

# ================= KINO QIDIRISH =================

@bot.message_handler(func=lambda m: True)
def send_movie(message):

    text = message.text.replace("/","")

    sql.execute("SELECT * FROM movies WHERE code=?", (text,))
    movie = sql.fetchone()

    if movie:

        views = movie[6] + 1

        sql.execute("UPDATE movies SET views=? WHERE code=?", (views,text))
        db.commit()

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("❤️ Saqlash",callback_data=f"fav_{text}")
        )

        bot.send_video(
        message.chat.id,
        movie[5],
        caption=f"""
🎬 {movie[1]}

📅 {movie[3]}
🎭 {movie[2]}

📊 Ko‘rishlar: {views}
⭐ Reyting: {movie[7]}
""",
        reply_markup=keyboard,
        protect_content=True
        )

        return

    sql.execute("SELECT code,name FROM movies WHERE name LIKE ?",('%'+text+'%',))

    res = sql.fetchall()

    if res:

        msg="🔎 Topilgan kinolar\n\n"

        for r in res:
            msg+=f"{r[0]} — {r[1]}\n"

        bot.send_message(message.chat.id,msg)

    else:

        bot.send_message(message.chat.id,"❌ Kino topilmadi")

print("Bot ishga tushdi...")
bot.infinity_polling()
