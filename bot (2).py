import telebot
from telebot import types

TOKEN = "8389171340:AAGflq0Tzt2hmT0AZvKLD859Rw9IPOFggmw"
OWNER_ID = 6784382795

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# =======================
#  WELCOME & GOODBYE FIX
# =======================

@bot.message_handler(content_types=["new_chat_members"])
def welcome_handler(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id,
        f"🎉 Welcome <b>{user.first_name}</b>! Enjoy your stay.")

@bot.message_handler(content_types=["left_chat_member"])
def goodbye_handler(message):
    left = message.left_chat_member
    bot.send_message(message.chat.id,
    f"👋 Goodbye <b>{left.first_name}</b>. Take care!")

# =======================
#  BOT ADDED TO GROUP
# =======================

@bot.my_chat_member_handler()
def bot_added(update: types.ChatMemberUpdated):

    old = update.old_chat_member.status
    new = update.new_chat_member.status

    if old in ["left", "kicked"] and new in ["member", "administrator"]:

        group_name = update.chat.title
        group_id = update.chat.id

        try:
            invite_link = bot.create_chat_invite_link(group_id).invite_link
        except:
            invite_link = "Bot not admin → Cannot fetch link"

        user = update.from_user

        bot.send_message(
            OWNER_ID,
            f"🤖 <b>Bot Added to Group</b>\n\n"
            f"👤 <b>Added by:</b> {user.first_name}\n"
            f"@{user.username}\n"
            f"🆔 {user.id}\n\n"
            f"👥 <b>Group:</b> {group_name}\n"
            f"🆔 {group_id}\n"
            f"🔗 {invite_link}"
        )

# =======================
#  /code MENU
# =======================

@bot.message_handler(commands=["code"])
def code_menu(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🎂 Birthday Card", "🎁 Surprise Card")
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=kb)

# =======================
#  BIRTHDAY COMMAND
# =======================

@bot.message_handler(commands=["birthday"])
def birthday_start(message):
    bot.send_message(message.chat.id, "🎂 Enter the celebrant's <b>Name</b>:")
    bot.register_next_step_handler(message, get_birthday_name)

def get_birthday_name(msg):
    name = msg.text
    bot.send_message(msg.chat.id, "📅 Enter the <b>Birthday Date</b>:")
    bot.register_next_step_handler(msg, get_birthday_date, name)

def get_birthday_date(msg, name):
    date = msg.text
    bot.send_message(msg.chat.id, "🎉 Enter the <b>Age</b>:")
    bot.register_next_step_handler(msg, get_birthday_age, name, date)

def get_birthday_age(msg, name, date):
    age = msg.text
    bot.send_message(msg.chat.id,
        "🖼 Upload the celebrant's photo using this link:\n"
        "👉 https://host-image-puce.vercel.app/\n\n"
        "Then paste the <b>image link</b> here:")
    bot.register_next_step_handler(msg, get_birthday_image, name, date, age)

def get_birthday_image(msg, name, date, age):
    image_url = msg.text
    bot.send_message(msg.chat.id, "💌 Enter your <b>Birthday Message</b>:")
    bot.register_next_step_handler(msg, generate_birthday_file, name, date, age, image_url)

def generate_birthday_file(msg, name, date, age, image_url):
    message_text = msg.text

    html_content = f"""
<html>
<body style="font-family: Arial; background: #ffe7f0; padding: 20px;">
<center>
<h1 style="color:#ff4da6;">🎉 HAPPY BIRTHDAY {name.upper()}! 🎉</h1>

<img src="{image_url}" width="250" style="border-radius:15px;"><br><br>

<h3>🌟 Name: {name}</h3>
<h3>🎂 Age: {age}</h3>
<h3>📅 Birthday: {date}</h3>

<div style="margin-top:20px; padding:15px; background:white; border-radius:10px; width:80%;">
<p><b>💌 Message:</b></p>
<p>{message_text}</p>
</div>
</center>
</body>
</html>
"""

    filename = f"birthday_{name}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Send file to user
    with open(filename, "rb") as f:
        bot.send_document(msg.chat.id, f, caption="🎂 Your Birthday Card")

    # Notify owner
    with open(filename, "rb") as f:
        bot.send_document(OWNER_ID, f, caption=f"🎂 Birthday card used by {msg.from_user.first_name} (@{msg.from_user.username})")

# =======================
#  SURPRISE COMMAND
# =======================

@bot.message_handler(commands=["surprise"])
def surprise_start(message):
    bot.send_message(message.chat.id, "🎁 Enter the <b>Name</b>:")
    bot.register_next_step_handler(message, get_surprise_name)

def get_surprise_name(msg):
    name = msg.text
    bot.send_message(msg.chat.id,
        "🖼 Upload the photo here:\n"
        "👉 https://host-image-puce.vercel.app/\n\n"
        "Then paste the <b>image link</b>:")
    bot.register_next_step_handler(msg, get_surprise_image, name)

def get_surprise_image(msg, name):
    image_url = msg.text
    bot.send_message(msg.chat.id, "💌 Enter your <b>Special Message</b>:")
    bot.register_next_step_handler(msg, generate_surprise_file, name, image_url)

def generate_surprise_file(msg, name, image_url):
    message_text = msg.text

    html_content = f"""
<html>
<body style="font-family: Arial; background:#e3f6ff; padding:20px;">
<center>
<h1 style="color:#008cff;">🎁 A LITTLE SURPRISE FOR YOU, {name.upper()}!</h1>

<img src="{image_url}" width="250" style="border-radius:15px;"><br><br>

<div style="margin-top:20px; padding:15px; background:white; border-radius:10px; width:80%;">
<p><b>💌 Message:</b></p>
<p>{message_text}</p>
</div>
</center>
</body>
</html>
"""

    filename = f"surprise_{name}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Send to user
    with open(filename, "rb") as f:
        bot.send_document(msg.chat.id, f, caption="🎁 Your Surprise Card")

    # Notify owner
    with open(filename, "rb") as f:
        bot.send_document(OWNER_ID, f, caption=f"🎁 Surprise card used by {msg.from_user.first_name} (@{msg.from_user.username})")

# =======================
#  START COMMAND
# =======================

@bot.message_handler(commands=["start"])
def start_cmd(message):
    bot.send_message(message.chat.id,
        "🤖 Bot Activated!\nUse /code to choose an action.")

# =======================
#  BOT RUN
# =======================

bot.infinity_polling(timeout=30, long_polling_timeout=30)
