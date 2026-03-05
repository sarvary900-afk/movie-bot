import telebot
import sqlite3

from config import TOKEN, ADMIN_ID, CHANNELS, UPLOAD_CHANNEL

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("kino.db", check_same_thread=False)
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS movies (
code TEXT,
name TEXT,
genre TEXT,
file_id TEXT,
views INTEGER,
premium INTEGER
)
""")

db.commit()

waiting_movie = {}


# START
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,"🎬 Kino kodini yuboring")


# ADMIN kino qo‘shish
@bot.message_handler(commands=['add'])
def add_movie(message):

    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split(" ")

    if len(args) < 4:
        bot.send_message(message.chat.id,"❌ Format:\n/add kod nom janr")
        return

    code = args[1]
    name = args[2]
    genre = args[3]

    waiting_movie[message.from_user.id] = (code,name,genre,0)

    bot.send_message(message.chat.id,"🎬 Endi kino videosini yuboring")


# VIDEO QABUL QILISH
@bot.message_handler(content_types=['video'])
def save_movie(message):

    if message.from_user.id in waiting_movie:

        code,name,genre,premium = waiting_movie[message.from_user.id]

        sql.execute(
        "INSERT INTO movies VALUES (?,?,?,?,?,?)",
        (code,name,genre,message.video.file_id,0,premium)
        )

        db.commit()

        bot.send_video(
            UPLOAD_CHANNEL,
            message.video.file_id,
            caption=f"🎬 {name}\n\n🔢 Kod: {code}"
        )

        del waiting_movie[message.from_user.id]

        bot.send_message(message.chat.id,"✅ Kino saqlandi va kanalga joylandi")


# KINO QIDIRISH
@bot.message_handler(func=lambda m: True)
def search_movie(message):

    code = message.text

    sql.execute("SELECT * FROM movies WHERE code=?",(code,))
    movie = sql.fetchone()

    if movie:

        sql.execute("UPDATE movies SET views = views + 1 WHERE code=?",(code,))
        db.commit()

        bot.send_video(
        message.chat.id,
        movie[3],
        caption=f"🎬 {movie[1]}"
        )

    else:
        bot.send_message(message.chat.id,"❌ Bunday kino topilmadi")


print("Bot ishga tushdi...")

bot.infinity_polling()
