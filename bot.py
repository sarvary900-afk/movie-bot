import telebot
import os
import json

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)

# 🔥 SENING TELEGRAM ID
ADMIN_ID = 6401247171

DATA_FILE = "movies.json"

# 🔹 JSON bazani yuklash
def load_movies():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# 🔹 JSON bazaga saqlash
def save_movies(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

movies = load_movies()
waiting_for_video = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Kino kodini yuboring 🎬")


# 🔥 ADMIN: kod kiritish
@bot.message_handler(commands=['add'])
def add_movie(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        code = message.text.split()[1]
        waiting_for_video[message.from_user.id] = code
        bot.reply_to(message, f"{code} kod uchun videoni yubor 🎬")
    except:
        bot.reply_to(message, "Foydalanish: /add 777")


# 🔥 ADMIN: video qabul qilish
@bot.message_handler(content_types=['video', 'document'])
def save_movie_handler(message):
    if message.from_user.id != ADMIN_ID:
        return

    if message.from_user.id in waiting_for_video:
        code = waiting_for_video[message.from_user.id]

        if message.video:
            file_id = message.video.file_id
        else:
            file_id = message.document.file_id

        movies[code] = file_id
        save_movies(movies)

        del waiting_for_video[message.from_user.id]

        bot.reply_to(message, f"{code} kodli kino saqlandi ✅")


# 🔥 Foydalanuvchi kod yuborsa
@bot.message_handler(func=lambda message: True, content_types=['text'])
def send_movie(message):
    code = message.text.strip()

    if code in movies:
        bot.send_video(message.chat.id, movies[code])
    else:
        bot.reply_to(message, "Bunday kod topilmadi ❌")


if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling()
