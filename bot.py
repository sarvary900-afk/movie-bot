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
    bot.infinity_polling()
