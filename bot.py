import telebot
import sqlite3
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TOKEN, ADMIN_ID, CHANNELS, UPLOAD_CHANNEL

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("kino.db", check_same_thread=False)
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS movies(
code TEXT,
name TEXT,
genre TEXT,
file_id TEXT,
views INTEGER
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS users(
user_id INTEGER
)""")

db.commit()

waiting_movie = {}
MOVIES_PER_PAGE = 10

# 🔐 OBUNA TEKSHIRISH
def check_sub(user_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left","kicked"]:
                return False
        except:
            return False
    return True


# 🔘 OBUNA TUGMALARI
def sub_keyboard():
    kb = InlineKeyboardMarkup()
    for ch in CHANNELS:
        kb.add(InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch.replace('@','')}"))
    kb.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub"))
    return kb


# 🚀 START
@bot.message_handler(commands=['start'])
def start(message):

    user = message.from_user.id

    sql.execute("SELECT user_id FROM users WHERE user_id=?", (user,))
    if not sql.fetchone():
        sql.execute("INSERT INTO users VALUES (?)",(user,))
        db.commit()

    if not check_sub(user):
        bot.send_message(
            message.chat.id,
            "❗ Kanallarga obuna bo‘ling:",
            reply_markup=sub_keyboard()
        )
        return

    bot.send_message(message.chat.id,"🎬 Kino kodini yuboring")


# 🔁 TEKSHIRISH TUGMASI
@bot.callback_query_handler(func=lambda call: call.data=="check_sub")
def check_button(call):

    if check_sub(call.from_user.id):
        bot.edit_message_text(
            "✅ Obuna tasdiqlandi!\n\n🎬 Endi kino kodini yuboring",
            call.message.chat.id,
            call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id,"❌ Hali obuna bo‘lmadingiz")


# ➕ ADMIN KINO QO‘SHISH
@bot.message_handler(commands=['add'])
def add_movie(message):

    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split(" ")

    if len(args) < 3:
        bot.send_message(message.chat.id,"❌ Format:\n/add kod nom")
        return

    code = args[1]
    name = " ".join(args[2:])

    waiting_movie[message.from_user.id] = (code,name,"Drama")

    bot.send_message(message.chat.id,"🎬 Videoni yubor")


# 🎥 VIDEO SAQLASH
@bot.message_handler(content_types=['video'])
def save_movie(message):

    if message.from_user.id in waiting_movie:

        code,name,genre = waiting_movie[message.from_user.id]

        sql.execute(
        "INSERT INTO movies VALUES (?,?,?,?,?)",
        (code,name,genre,message.video.file_id,0)
        )

        db.commit()

        # kanalga yuborish
        bot.send_video(
            UPLOAD_CHANNEL,
            message.video.file_id,
            caption=f"🎬 {name}\n\n🔢 Kod: {code}"
        )

        del waiting_movie[message.from_user.id]

        bot.send_message(message.chat.id,"✅ Saqlandi va kanalga joylandi")


# 🔍 QIDIRISH
@bot.message_handler(func=lambda m: True)
def search(message):

    text = message.text

    # kod bo‘yicha
    sql.execute("SELECT * FROM movies WHERE code=?", (text,))
    movie = sql.fetchone()

    if movie:

        sql.execute("UPDATE movies SET views=views+1 WHERE code=?", (text,))
        db.commit()

        bot.send_video(
            message.chat.id,
            movie[3],
            caption=f"🎬 {movie[1]}\n📊 {movie[4]+1} marta ko‘rilgan"
        )
        return

    # nom bo‘yicha
    sql.execute("SELECT code,name FROM movies WHERE name LIKE ?",('%'+text+'%',))
    res = sql.fetchall()

    if res:
        msg="🔎 Topildi:\n\n"
        for r in res:
            msg+=f"{r[0]} — {r[1]}\n"
        bot.send_message(message.chat.id,msg)
    else:
        bot.send_message(message.chat.id,"❌ Topilmadi")


# 🏆 TOP
@bot.message_handler(commands=['top'])
def top(message):

    sql.execute("SELECT name,views FROM movies ORDER BY views DESC LIMIT 10")
    movies = sql.fetchall()

    text="🏆 TOP kinolar\n\n"
    for i,m in enumerate(movies,1):
        text+=f"{i}. {m[0]} — {m[1]}\n"

    bot.send_message(message.chat.id,text)


# 🎲 RANDOM
@bot.message_handler(commands=['random'])
def random_movie(message):

    sql.execute("SELECT * FROM movies")
    movies = sql.fetchall()

    if movies:
        m = random.choice(movies)
        bot.send_video(message.chat.id,m[3],caption=m[1])


# 📊 STATS
@bot.message_handler(commands=['stats'])
def stats(message):

    if message.from_user.id != ADMIN_ID:
        return

    sql.execute("SELECT COUNT(*) FROM users")
    users = sql.fetchone()[0]

    sql.execute("SELECT COUNT(*) FROM movies")
    movies = sql.fetchone()[0]

    bot.send_message(message.chat.id,f"👥 {users} user\n🎬 {movies} kino")


# 🗑 O‘CHIRISH
@bot.message_handler(commands=['del'])
def delete(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        code = message.text.split()[1]
        sql.execute("DELETE FROM movies WHERE code=?", (code,))
        db.commit()
        bot.send_message(message.chat.id,"🗑 O‘chirildi")
    except:
        bot.send_message(message.chat.id,"❌ /del 123")


# 📢 BROADCAST
@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/broadcast ","")

    sql.execute("SELECT user_id FROM users")
    users = sql.fetchall()

    for u in users:
        try:
            bot.send_message(u[0],text)
        except:
            pass

    bot.send_message(message.chat.id,"✅ Yuborildi")


print("Bot ishga tushdi 🚀")
bot.infinity_polling()
