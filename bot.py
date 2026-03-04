import telebot
import os
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6401247171

CHANNELS = [
    "@Dramalar_olami_uzz",
    "@trend_muzikalar_uz_01"
]

DATA_FILE = "movies.json"

# ================== DATA FUNCTIONS ==================

def load_movies():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_movies(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

movies = load_movies()
waiting_for_video = {}

# ================== SUBSCRIPTION CHECK ==================

def is_subscribed(user_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def subscribe_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📢 1-kanal", url="https://t.me/Dramalar_olami_uzz")
    )
    markup.add(
        InlineKeyboardButton("📢 2-kanal", url="https://t.me/trend_muzikalar_uz_01")
    )
    markup.add(
        InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
    )
    return markup

# ================== START ==================

@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❗ Iltimos kanallarga obuna bo‘ling:",
            reply_markup=subscribe_keyboard()
        )
        return

    bot.send_message(message.chat.id, "🎬 Kino kodini yuboring")

# ================== CHECK BUTTON ==================

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "Obuna tasdiqlandi ✅")
        bot.send_message(call.message.chat.id, "🎬 Endi kino kodini yuboring")
    else:
        bot.answer_callback_query(call.id, "Hali obuna bo‘lmagansiz ❌")

# ================== ADD MOVIE ==================

@bot.message_handler(commands=['add'])
def add_movie(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(" ", 2)
        code = parts[1]
        name = parts[2]

        waiting_for_video[message.from_user.id] = (code, name)

        bot.reply_to(message, f"🎬 '{name}' uchun videoni yubor")
    except:
        bot.reply_to(message, "Foydalanish:\n/add 101 Dune Part Two")

# ================== SAVE MOVIE FILE ==================

@bot.message_handler(content_types=['video', 'document'])
def save_movie_handler(message):
    if message.from_user.id != ADMIN_ID:
        return

    if message.from_user.id in waiting_for_video:
        code, name = waiting_for_video[message.from_user.id]

        if message.video:
            file_id = message.video.file_id
        else:
            file_id = message.document.file_id

        movies[code] = {
            "name": name,
            "file_id": file_id,
            "views": 0
        }

        save_movies(movies)
        del waiting_for_video[message.from_user.id]

        bot.reply_to(message, f"✅ '{name}' saqlandi")

# ================== SEND MOVIE ==================

@bot.message_handler(func=lambda message: True, content_types=['text'])
def send_movie(message):

    if not is_subscribed(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❗ Obuna bo‘lmasangiz kino berilmaydi",
            reply_markup=subscribe_keyboard()
        )
        return

    code = message.text.strip()

    if code in movies:
        movies[code]["views"] += 1
        save_movies(movies)

        caption = f"""
🎬 {movies[code]['name']}

🔥 Qidirilgan: {movies[code]['views']} marta
"""

        bot.send_video(
            message.chat.id,
            movies[code]["file_id"],
            caption=caption
        )
    else:
        bot.reply_to(message, "❌ Bunday kod topilmadi")

# ================== RUN ==================

print("Bot ishga tushdi...")
bot.infinity_polling()
