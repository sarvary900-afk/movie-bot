import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Kino kodini yuboring 🎬")


# 🔹 FILE_ID olish
@bot.message_handler(content_types=['video', 'document'])
def get_file_id(message):
    if message.video:
        file_id = message.video.file_id
    else:
        file_id = message.document.file_id

    bot.reply_to(message, f"FILE_ID:\n{file_id}")


# 🔹 Kod orqali kino yuborish
@bot.message_handler(func=lambda message: True, content_types=['text'])
def send_movie(message):
    code = message.text

    movies = {
        "100": "BU_YERGA_FILE_ID"
    }

    if code in movies:
        bot.send_video(message.chat.id, movies[code])
    else:
        bot.reply_to(message, "Bunday kod topilmadi ❌")


if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling()
