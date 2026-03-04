import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Kino kodini yuboring 🎬")

@bot.message_handler(func=lambda message: True)
def send_movie(message):
    code = message.text

    movies = {
        "100": "Bu yerga kino linkini qo'yasiz",
        "200": "Bu yerga boshqa kino linki"
    }

    if code in movies:
        bot.reply_to(message, movies[code])
    else:
        bot.reply_to(message, "Bunday kod topilmadi ❌")

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    @bot.message_handler(content_types=['video', 'document'])
def get_file_id(message):
    if message.video:
        file_id = message.video.file_id
    else:
        file_id = message.document.file_id

    bot.reply_to(message, f"FILE_ID:\n{file_id}") bot.infinity_polling()
