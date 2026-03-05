import telebot
from telebot import types

BOT_TOKEN = "8288853849:AAG55nlWKoR1fYm-HoNOargMvHTdmbg8wxw"

bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_ID = 6401247171

CHANNELS = [
"@Dramalar_olami_uzz",
"@trend_muzikalar_uz_01"
]

movies = {
"777": {
"name": "Test Kino",
"file_id": "BAACAgEAAxkBAAMGaahynCZPu32jml-N6gr35uXbuaEAAqQJAAImbzFFwH61tu76gxQ6BA",
"views": 0
}
}

def check_sub(user_id):
    for channel in CHANNELS:
        status = bot.get_chat_member(channel, user_id).status
        if status not in ["member","administrator","creator"]:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,"🎬 Kino kodini yuboring")

@bot.message_handler(commands=['add'])
def add_movie(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id,"Kino kodi va nomini yuboring:\nMasalan: 101|Avatar")

@bot.message_handler(func=lambda m: "|" in m.text and m.from_user.id == ADMIN_ID)
def get_movie_info(message):
    code,name = message.text.split("|")
    movies[code] = {"name":name,"file_id":None,"views":0}
    bot.send_message(message.chat.id,"Endi kino videosini yuboring")

@bot.message_handler(content_types=['video'])
def save_video(message):
    if message.from_user.id != ADMIN_ID:
        return
    file_id = message.video.file_id
    for code in movies:
        if movies[code]["file_id"] is None:
            movies[code]["file_id"] = file_id
            bot.send_message(message.chat.id,f"Kino qo‘shildi ✅\nKod: {code}")
            break

@bot.message_handler(func=lambda m: True)
def send_movie(message):
    user_id = message.from_user.id
    
    if not check_sub(user_id):
        bot.send_message(message.chat.id,"❌ Avval kanallarga obuna bo‘ling")
        return
    
    code = message.text
    
    if code in movies:
        movies[code]["views"] += 1
        
        name = movies[code]["name"]
        views = movies[code]["views"]
        file_id = movies[code]["file_id"]
        
        bot.send_message(message.chat.id,f"🎬 {name}\n📊 Qidirilgan: {views} marta")
        bot.send_video(message.chat.id,file_id)
        
    else:
        bot.send_message(message.chat.id,"❌ Bunday kino topilmadi")

bot.infinity_polling()
