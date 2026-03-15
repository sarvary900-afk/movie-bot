import telebot
import sqlite3
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_ID, KANALLAR, UPLOAD_CHANNEL

bot = telebot.TeleBot(BOT_TOKEN)

# --------- DATABASE ---------
db = sqlite3.connect("kino.db", check_same_thread=False)
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS movies(
code TEXT,
name TEXT,
genre TEXT,
file_id TEXT,
views INTEGER,
premium INTEGER
)
""")

sql.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER
)
""")

db.commit()

waiting_movie = {}
MOVIES_PER_PAGE = 10

# --------- OBUNA TEKSHIRISH ---------
def check_sub(user_id):
    for ch in KANALLAR:
        try:
            status = bot.get_chat_member(ch["url"], user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# --------- START ---------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    sql.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not sql.fetchone():
        sql.execute("INSERT INTO users VALUES (?)", (user_id,))
        db.commit()

    if not check_sub(user_id):
        text = "❗ Botimiz to‘liq ishlashi uchun ushbu kanallarga obuna bo‘ling:\n\n"
        keyboard = InlineKeyboardMarkup(row_width=1)
        for ch in KANALLAR:
            keyboard.add(InlineKeyboardButton(text=ch["name"], url=ch["url"]))
        keyboard.add(InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_channels"))
        bot.send_message(message.chat.id, text, reply_markup=keyboard)
        return

    bot.send_message(message.chat.id, "🎬 Kino kodini yuboring")

# --------- TEKSHIRISH TUGMASI ---------
@bot.callback_query_handler(func=lambda call: call.data == "check_channels")
def check_channels(call):
    user_id = call.from_user.id
    if check_sub(user_id):
        bot.send_message(call.message.chat.id, "✅ Siz barcha kanallarga obuna bo‘ldingiz!\n🎬 Kino kodini yuboring")
    else:
        bot.send_message(call.message.chat.id, "❌ Iltimos, barcha kanallarga obuna bo‘ling va qayta tekshiring")

# --------- ADMIN KINO QO‘SHISH ---------
@bot.message_handler(commands=['add'])
def add_movie(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split(" ", 2)
    if len(args) < 3:
        bot.send_message(message.chat.id, "❌ Format:\n/add kod nomi")
        return
    code = args[1]
    name = args[2]
    waiting_movie[message.from_user.id] = (code, name, "Drama", 0)
    bot.send_message(message.chat.id, "🎬 Endi kino videosini yuboring")

# --------- VIDEO QABUL QILISH ---------
@bot.message_handler(content_types=['video'])
def save_movie(message):
    if message.from_user.id in waiting_movie:
        code, name, genre, premium = waiting_movie[message.from_user.id]
        sql.execute(
            "INSERT INTO movies VALUES (?,?,?,?,?,?)",
            (code, name, genre, message.video.file_id, 0, premium)
        )
        db.commit()
        bot.send_video(
            UPLOAD_CHANNEL,
            message.video.file_id,
            caption=f"🎬 {name}\n\n🔢 Kod: {code}"
        )
        del waiting_movie[message.from_user.id]
        bot.send_message(message.chat.id, "✅ Kino saqlandi va kanalga joylandi")

# --------- MUNDARIJA ---------
@bot.message_handler(commands=['list'])
def list_movies(message):
    show_page(message.chat.id, 1)

def show_page(chat_id, page):
    offset = (page - 1) * MOVIES_PER_PAGE
    sql.execute(
        "SELECT code,name FROM movies LIMIT ? OFFSET ?",
        (MOVIES_PER_PAGE, offset)
    )
    movies = sql.fetchall()
    text = f"🎬 Kino mundarijasi ({page}-bet)\n\n"
    for m in movies:
        text += f"{m[0]} — {m[1]}\n"
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("⬅️", callback_data=f"page_{page-1}"),
        InlineKeyboardButton(str(page), callback_data="none"),
        InlineKeyboardButton("➡️", callback_data=f"page_{page+1}")
    )
    bot.send_message(chat_id, text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def page_callback(call):
    page = int(call.data.split("_")[1])
    if page < 1:
        return
    show_page(call.message.chat.id, page)

# --------- TOP KINOLAR ---------
@bot.message_handler(commands=['top'])
def top_movies(message):
    sql.execute("SELECT name,views FROM movies ORDER BY views DESC LIMIT 10")
    movies = sql.fetchall()
    text = "🏆 TOP 10 kinolar\n\n"
    for i, m in enumerate(movies, 1):
        text += f"{i}. {m[0]} — {m[1]} qidiruv\n"
    bot.send_message(message.chat.id, text)

# --------- RANDOM KINO ---------
@bot.message_handler(commands=['random'])
def random_movie(message):
    sql.execute("SELECT * FROM movies")
    movies = sql.fetchall()
    if movies:
        movie = random.choice(movies)
        bot.send_video(
            message.chat.id,
            movie[3],
            caption=f"🎬 {movie[1]}",
            protect_content=True
        )

# --------- STATISTIKA ---------
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    sql.execute("SELECT COUNT(*) FROM users")
    users = sql.fetchone()[0]
    sql.execute("SELECT COUNT(*) FROM movies")
    movies = sql.fetchone()[0]
    bot.send_message(message.chat.id, f"👥 Userlar: {users}\n🎬 Kinolar: {movies}")

# --------- KINO O‘CHIRISH ---------
@bot.message_handler(commands=['del'])
def delete_movie(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        code = message.text.split()[1]
        sql.execute("DELETE FROM movies WHERE code=?", (code,))
        db.commit()
        bot.send_message(message.chat.id, "🗑 Kino o‘chirildi")
    except:
        bot.send_message(message.chat.id, "❌ /del 123 format")

# --------- BROADCAST ---------
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
    bot.send_message(message.chat.id, "✅ Reklama yuborildi")

# --------- KINO QIDIRISH ---------
@bot.message_handler(func=lambda m: True)
def send_movie(message):
    text = message.text.replace("/","")
    sql.execute("SELECT * FROM movies WHERE code=?", (text,))
    movie = sql.fetchone()
    if movie:
        views = movie[4] + 1
        sql.execute("UPDATE movies SET views=? WHERE code=?", (views, text))
        db.commit()
        bot.send_video(
            message.chat.id,
            movie[3],
            caption=f"🎬 {movie[1]}\n\n📊 Qidirilgan: {views}",
            protect_content=True
        )
        return

    sql.execute("SELECT code,name FROM movies WHERE name LIKE ?", ('%'+text+'%',))
    res = sql.fetchall()
    if res:
        msg = "🔎 Topilgan kinolar\n\n"
        for r in res:
            msg += f"{r[0]} — {r[1]}\n"
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, "❌ Kino topilmadi")

print("Bot ishga tushdi...")

bot.infinity_polling()
