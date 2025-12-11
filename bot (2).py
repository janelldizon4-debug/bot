import telebot
from telebot import types

TOKEN = "8389171340:AAGflq0Tzt2hmT0AZvKLD859Rw9IPOFggmw"
OWNER_ID = 6784382795

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# =====================================================
#  /code MENU
# =====================================================

@bot.message_handler(commands=["code"])
def code_menu(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🎂 Birthday Card", "🎁 Surprise Card")
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=kb)


# =====================================================
#  BIRTHDAY FLOW (BUTTON + COMMAND)
# =====================================================

@bot.message_handler(commands=["birthday"])
@bot.message_handler(func=lambda msg: msg.text == "🎂 Birthday Card")
def birthday_start(message):
    bot.send_message(message.chat.id, "🎂 Enter the celebrant’s Name:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, birthday_get_name)

def birthday_get_name(msg):
    name = msg.text
    bot.send_message(msg.chat.id, "📅 Enter the Date of Birthday:")
    bot.register_next_step_handler(msg, birthday_get_date, name)

def birthday_get_date(msg, name):
    date = msg.text
    bot.send_message(msg.chat.id, "🎉 Enter the Age of Celebrant:")
    bot.register_next_step_handler(msg, birthday_get_age, name, date)

def birthday_get_age(msg, name, date):
    age = msg.text
    bot.send_message(msg.chat.id,
        "🖼 Upload the photo here:\n"
        "👉 https://host-image-puce.vercel.app/\n\n"
        "Then send the Photo Link here:")
    bot.register_next_step_handler(msg, birthday_get_image, name, date, age)

def birthday_get_image(msg, name, date, age):
    image_url = msg.text
    bot.send_message(msg.chat.id, "💌 Enter your Birthday Message:")
    bot.register_next_step_handler(msg, birthday_generate_file, name, date, age, image_url)

def birthday_generate_file(msg, name, date, age, image_url):
    message_text = msg.text

    html = f"""
<html>
<body style="font-family:Arial; background:#ffe7f0; padding:20px;">
<center>
<h1 style="color:#ff4da6;">🎉 HAPPY BIRTHDAY {name.upper()}! 🎉</h1>
<img src="{image_url}" width="250" style="border-radius:15px;"><br><br>

<h3>🌟 Name: {name}</h3>
<h3>🎂 Age: {age}</h3>
<h3>📅 Birthday: {date}</h3>

<div style="padding:15px; background:white; border-radius:10px; width:80%;">
<b>💌 Message:</b>
<p>{message_text}</p>
</div>

</center>
</body>
</html>
"""

    filename = f"birthday_{name}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    # Send HTML to user
    with open(filename, "rb") as f:
        bot.send_document(msg.chat.id, f, caption="🎂 Your Birthday Card")

    # Send HTML + info to owner
    with open(filename, "rb") as f:
        bot.send_document(
            OWNER_ID, f,
            caption=f"🎂 Birthday card made by {msg.from_user.first_name} (@{msg.from_user.username})"
        )


# =====================================================
#  SURPRISE FLOW (BUTTON + COMMAND)
# =====================================================

@bot.message_handler(commands=["surprise"])
@bot.message_handler(func=lambda msg: msg.text == "🎁 Surprise Card")
def surprise_start(message):
    bot.send_message(message.chat.id, "🎁 Enter the Name:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, surprise_get_name)

def surprise_get_name(msg):
    name = msg.text
    bot.send_message(msg.chat.id,
        "🖼 Upload photo here:\n"
        "👉 https://host-image-puce.vercel.app/\n\n"
        "Then send the Photo Link here:")
    bot.register_next_step_handler(msg, surprise_get_image, name)

def surprise_get_image(msg, name):
    image_url = msg.text
    bot.send_message(msg.chat.id, "💌 Enter your Special Message:")
    bot.register_next_step_handler(msg, surprise_generate_file, name, image_url)

def surprise_generate_file(msg, name, image_url):
    message_text = msg.text

    html = f"""
<html>
<body style="font-family:Arial; background:#e3f6ff; padding:20px;">
<center>
<h1 style="color:#008cff;">🎁 A LITTLE SURPRISE FOR YOU, {name.upper()}!</h1>
<img src="{image_url}" width="250" style="border-radius:15px;"><br><br>

<div style="padding:15px; background:white; border-radius:10px; width:80%;">
<b>💌 Message:</b>
<p>{message_text}</p>
</div>

</center>
</body>
</html>
"""

    filename = f"surprise_{name}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    # Send HTML to user
    with open(filename, "rb") as f:
        bot.send_document(msg.chat.id, f, caption="🎁 Your Surprise Card")

    # Notify owner + file
    with open(filename, "rb") as f:
        bot.send_document(
            OWNER_ID, f,
            caption=f"🎁 Surprise card made by {msg.from_user.first_name} (@{msg.from_user.username})"
        )


# =====================================================
#  START COMMAND
# =====================================================

@bot.message_handler(commands=["start"])
def start_cmd(message):
    bot.send_message(message.chat.id, "🤖 Bot Activated!\nUse /code to choose an action.")


# =====================================================
#  RUN BOT
# =====================================================

bot.infinity_polling(timeout=30, long_polling_timeout=30)
