import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TOKEN,CHANNELS
from users import add_user
from movies import *
from admin import *

bot = telebot.TeleBot(TOKEN)

waiting_movie={}


def check_sub(bot,user):

    for ch in CHANNELS:

        try:

            status=bot.get_chat_member(ch,user).status

            if status not in ["member","administrator","creator"]:
                return False

        except:
            return False

    return True


@bot.message_handler(commands=['start'])
def start(message):

    user=message.from_user.id

    ref=None

    try:
        ref=int(message.text.split()[1])
    except:
        pass

    add_user(user,ref)

    if not check_sub(bot,user):

        text="❗ Kanallarga obuna bo‘ling\n\n"

        keyboard=InlineKeyboardMarkup()

        for ch in CHANNELS:

            text+=f"{ch}\n"

            keyboard.add(
            InlineKeyboardButton(
            "📢 Kanal",
            url=f"https://t.me/{ch.replace('@','')}"
            )
            )

        bot.send_message(message.chat.id,text,reply_markup=keyboard)

        return

    bot.send_message(message.chat.id,"🎬 Kino kodini yuboring")


@bot.message_handler(func=lambda m: m.text.startswith("/"))
def add_movie_cmd(message):

    if not is_admin(message.from_user.id):
        return

    try:

        text=message.text[1:]

        code,name=text.split(" ",1)

        waiting_movie[message.from_user.id]=(code,name)

        bot.send_message(message.chat.id,"🎬 Endi kino videosini yuboring")

    except:

        bot.send_message(message.chat.id,"❌ Format:\n/256 Kino nomi")


@bot.message_handler(content_types=['video'])
def save_movie(message):

    if message.from_user.id in waiting_movie:

        code,name=waiting_movie[message.from_user.id]

        add_movie(code,name,"Drama",message.video.file_id)

        del waiting_movie[message.from_user.id]

        bot.send_message(message.chat.id,"✅ Kino saqlandi")


@bot.message_handler(commands=['top'])
def top(message):

    movies=top_movies()

    text="🏆 TOP kinolar\n\n"

    for i,m in enumerate(movies,1):

        text+=f"{i}. {m[0]} — {m[1]}\n"

    bot.send_message(message.chat.id,text)


@bot.message_handler(commands=['random'])
def random_cmd(message):

    movie=random_movie()

    if movie:

        bot.send_video(
        message.chat.id,
        movie[3],
        caption=f"🎬 {movie[1]}",
        protect_content=True
        )


@bot.message_handler(commands=['new'])
def new_cmd(message):

    movies=new_movies()

    text="🔥 Yangi kinolar\n\n"

    for m in movies:
        text+=f"{m[0]} — {m[1]}\n"

    bot.send_message(message.chat.id,text)


@bot.message_handler(commands=['stats'])
def stats(message):

    if not is_admin(message.from_user.id):
        return

    count=user_count()

    bot.send_message(message.chat.id,f"👥 Userlar: {count}")


@bot.message_handler(func=lambda m: True)
def send_movie(message):

    movie=get_movie(message.text)

    if movie:

        bot.send_video(
        message.chat.id,
        movie[3],
        caption=f"🎬 {movie[1]}",
        protect_content=True
        )

        return

    res=search_movie(message.text)

    if res:

        msg="🔎 Topilgan kinolar\n\n"

        for r in res:
            msg+=f"{r[0]} — {r[1]}\n"

        bot.send_message(message.chat.id,msg)

    else:

        bot.send_message(message.chat.id,"❌ Kino topilmadi")


bot.infinity_polling()
