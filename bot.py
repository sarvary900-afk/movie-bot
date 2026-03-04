import telebot
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8288853849:AAG55nlWKoR1fYm-HoNOargMvHTdmbg8wxw"
ADMIN_ID = 6401247171

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DATA_FILE = "movies.json"

CHANNELS = [
    "@Dramalar_olami_uzz",
    "@trend_muzikalar_uz_01"
]

user_subscribe_message = {}

# ================= SAFE JSON LOAD =================

def load_movies():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_movies(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

movies = load_movies()

# ================= SUB CHECK =================

def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def subscribe_panel(chat_id, user_id):

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📢 Dramalar olami", url="https://t.me/Dramalar_olami_uzz")
    )
    markup.add(
        InlineKeyboardButton("📢 Trend muzikalar", url="https://t.me/trend_muzikalar_uz_01")
    )
    markup.add(
        InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
    )

    if user_id in user_subscribe_message:
        try:
            bot.delete_message(chat_id, user_subscribe_message[user_id])
        except:
            pass

    msg = bot.send_message(
        chat_id,
        "❗ IKKALA kanalga ham obuna bo‘ling.",
        reply_markup=markup
    )

    user_subscribe_message[user_id] = msg.message_id

# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):

    if not check_subscription(message.from_user.id):
        subscribe_panel(message.chat.id, message.from_user.id)
        return

    bot.send_message(message.chat.id, "🎬 Kino kodini yuboring")

# ================= CHECK BUTTON =================

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):

    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if check_subscription(user_id):

        if user_id in user_subscribe_message:
            try:
                bot.delete_message(chat_id, user_subscribe_message[user_id])
            except:
                pass
            del user_subscribe_message[user_id]

        bot.send_message(chat_id, "✅ Obuna tasdiqlandi!\n\n🎬 Endi kino kodini yuboring.")
    else:
        bot.answer_callback_query(call.id, "❌ Ikkala kanalga ham obuna bo‘ling", show_alert=True)

# ================= SEND MOVIE =================

@bot.message_handler(func=lambda message: message.text and message.text.isdigit())
def send_movie(message):

    if not check_subscription(message.from_user.id):
        subscribe_panel(message.chat.id, message.from_user.id)
        return

    code = message.text

    if code not in movies:
        bot.reply_to(message, "❌ Bunday kod topilmadi.")
        return

    movies[code]["views"] += 1
    movies[code]["weekly_views"] += 1
    save_movies(movies)

    data = movies[code]

    caption = f"""
🎬 <b>{data['name']}</b>

🎭 Janr: {data['genre']}
⭐ Reyting: {data['rating']}

📝 {data['description']}

🔥 Jami qidirilgan: {data['views']} marta
📈 7 kunlik trend: {data['weekly_views']} marta

🔒 @SHAKH_345
"""

    bot.send_photo(message.chat.id, data["poster_id"])
    bot.send_video(
        message.chat.id,
        data["file_id"],
        caption=caption,
        protect_content=True
    )

# ================= RUN =================

bot.infinity_polling(skip_pending=True)
