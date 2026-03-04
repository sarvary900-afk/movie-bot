import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)


# 🎬 Kino bazasi
movies = {
    "777": "BAACAgEAAxkBAAMGaahynCZPu32jml-N6gr35uXbuaEAAqQJAAImbzFFwH61tu76gxQ6BA"
}


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Kino kodini yuboring 🎬")


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
