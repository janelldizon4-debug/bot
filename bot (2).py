import telebot
from telebot import types

TOKEN = "8389171340:AAGflq0Tzt2hmT0AZvKLD859Rw9IPOFggmw"
OWNER_ID = 6784382795   # <-- Your Telegram ID

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ========= NOTIFY OWNER WHEN BOT IS ADDED TO A GROUP ========= #

@bot.my_chat_member_handler()
def bot_added_handler(update: types.ChatMemberUpdated):
    old = update.old_chat_member.status
    new = update.new_chat_member.status

    # When bot is added to a group
    if old in ["left", "kicked"] and new in ["member", "administrator"]:
        group_name = update.chat.title
        group_id = update.chat.id

        # Try to get group invite link (only if bot is admin)
        try:
            invite_link = bot.create_chat_invite_link(group_id).invite_link
        except:
            invite_link = "No access / Bot is not admin"

        user = update.from_user

        text = (
            f"🤖 <b>Your bot was added to a new group!</b>\n\n"
            f"👤 <b>Added by:</b> {user.first_name}\n"
            f"🔹 Username: @{user.username}\n"
            f"🆔 User ID: {user.id}\n\n"
            f"👥 <b>Group Name:</b> {group_name}\n"
            f"🆔 Group ID: {group_id}\n"
            f"🔗 <b>Group Link:</b> {invite_link}"
        )

        bot.send_message(OWNER_ID, text)

# ========= WELCOME / GOODBYE HANDLERS ========= #

@bot.chat_member_handler()
def handle_member_update(message: types.ChatMemberUpdated):
    old = message.old_chat_member
    new = message.new_chat_member

    # User joined
    if old.status in ["left", "kicked"] and new.status in ["member", "administrator"]:
        bot.send_message(
            message.chat.id,
            f"🎉 Welcome <b>{new.user.first_name}</b>!\nGlad to have you here."
        )

    # User left
    if old.status in ["member", "administrator"] and new.status in ["left", "kicked"]:
        bot.send_message(
            message.chat.id,
            f"👋 Goodbye <b>{old.user.first_name}</b>.\nWe’ll miss you!"
        )

# ========= BIRTHDAY COMMAND ========= #

@bot.message_handler(commands=["birthday"])
def birthday_card(message):
    bot.send_message(message.chat.id,
                     "🎂 Please enter the celebrant's *Name*:")
    bot.register_next_step_handler(message, get_bday_name)


def get_bday_name(msg):
    name = msg.text
    bot.send_message(msg.chat.id, "📅 Enter Birthday Date (ex: Feb 14, 2025):")
    bot.register_next_step_handler(msg, get_bday_date, name)


def get_bday_date(msg, name):
    date = msg.text
    bot.send_message(msg.chat.id, "🎉 Enter Age:")
    bot.register_next_step_handler(msg, build_birthday_card, name, date)


def build_birthday_card(msg, name, date):
    age = msg.text

    card = f"""
<b><i>🎉 HAPPY BIRTHDAY {name.upper()}! 🎉</i></b>

🌟 <b>Name:</b> {name}
🎂 <b>Age:</b> {age}
📅 <b>Birthday:</b> {date}

———————————————
<b><i>Your Birthday Message:</i></b>
<code>[ Write your birthday message here ]</code>
———————————————

<img src='https://i.imgur.com/VDfEo4X.png'>
"""

    bot.send_message(msg.chat.id, card)

    bot.send_message(
        OWNER_ID,
        f"🎂 <b>/birthday used by:</b>\n"
        f"Name: {msg.from_user.first_name}\n"
        f"Username: @{msg.from_user.username}\n"
        f"ID: {msg.from_user.id}\n\n"
        f"<b>Target Celebrant:</b> {name}\n"
        f"<b>Birthday:</b> {date}, Age: {age}"
    )

# ========= SURPRISE COMMAND ========= #

@bot.message_handler(commands=["surprise"])
def surprise_card(message):
    bot.send_message(message.chat.id,
                     "🎁 Enter Name of the Person for the Surprise:")
    bot.register_next_step_handler(message, build_surprise_card)


def build_surprise_card(msg):
    name = msg.text

    card = f"""
🎁 <b><i>A LITTLE SURPRISE FOR YOU, {name.upper()}!</i></b>

———————————————
<b>Your Special Message:</b>
<code>[ Write your surprise message here ]</code>
———————————————

<img src='https://i.imgur.com/J2bWNE7.png'>
"""

    bot.send_message(msg.chat.id, card)

    bot.send_message(
        OWNER_ID,
        f"🎁 <b>/surprise used by:</b>\n"
        f"Name: {msg.from_user.first_name}\n"
        f"Username: @{msg.from_user.username}\n"
        f"ID: {msg.from_user.id}\n"
        f"Surprise For: {name}"
    )

# ========= START ========= #

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "🤖 <b>Bot Activated!</b>\nUse /birthday or /surprise."
    )

bot.infinity_polling()
