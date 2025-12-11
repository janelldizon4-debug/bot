import telebot
from telebot import types
import json
import threading
import time
import re

TOKEN = "8389171340:AAGflq0Tzt2hmT0AZvKLD859Rw9IPOFggmw"
OWNER_ID = 6784382795
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# =====================================================
#  REGISTERED USERS STORED INSIDE THIS FILE
# =====================================================

registered_users = [6784382795]   # <-- Your ID is always first


# =====================================================
#  SAVE UPDATED USER LIST INTO THIS SAME FILE
# =====================================================

def update_script():
    """Rewrite THIS FILE with updated registered_users."""
    with open(__file__, "r", encoding="utf-8") as f:
        content = f.read()

    new_list = json.dumps(registered_users)

    updated = re.sub(
        r"registered_users = \[.*?\]",
        f"registered_users = {new_list}",
        content,
        flags=re.DOTALL
    )

    with open(__file__, "w", encoding="utf-8") as f:
        f.write(updated)


# =====================================================
#  CHECK OWNER
# =====================================================

def is_owner(uid):
    return uid == OWNER_ID


# =====================================================
#  AUTO-BAN UNREGISTERED USERS
# =====================================================

@bot.chat_member_handler()
def on_user_join(update: types.ChatMemberUpdated):

    user = update.new_chat_member.user

    if update.new_chat_member.status == "member":
        if user.id not in registered_users:

            # Ban immediately
            try:
                bot.ban_chat_member(update.chat.id, user.id)
            except:
                pass

            # Notify owner
            bot.send_message(
                OWNER_ID,
                f"⛔ <b>Unregistered user banned</b>\n"
                f"Name: {user.first_name}\n"
                f"ID: {user.id}"
            )


# =====================================================
#  DELETE MESSAGES FROM UNREGISTERED USERS
# =====================================================

@bot.message_handler(func=lambda m: True, content_types=["text", "photo", "video", "document", "audio"])
def delete_unregistered(message):
    if message.from_user.id not in registered_users:
        try:
            bot.delete_message(message.chat.id, message.id)
        except:
            pass
        return


# =====================================================
#  WELCOME & GOODBYE
# =====================================================

@bot.message_handler(content_types=["new_chat_members"])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id, f"🎉 Welcome <b>{user.first_name}</b>!")

@bot.message_handler(content_types=["left_chat_member"])
def goodbye(message):
    bot.send_message(message.chat.id, f"👋 Goodbye <b>{message.left_chat_member.first_name}</b>!")


# =====================================================
#  BOT ADDED TO GROUP LOG
# =====================================================

@bot.my_chat_member_handler()
def bot_added(update: types.ChatMemberUpdated):

    old = update.old_chat_member.status
    new = update.new_chat_member.status

    if old in ["left", "kicked"] and new in ["member", "administrator"]:

        chat = update.chat
        user = update.from_user

        try:
            link = bot.create_chat_invite_link(chat.id).invite_link
        except:
            link = "Bot not admin"

        bot.send_message(
            OWNER_ID,
            f"🤖 <b>Bot added to a new group</b>\n\n"
            f"👥 {chat.title}\n"
            f"🆔 {chat.id}\n"
            f"🔗 {link}\n\n"
            f"👤 Added by {user.first_name} (@{user.username})\n"
            f"🆔 {user.id}"
        )


# =====================================================
#  OWNER COMMANDS
# =====================================================

@bot.message_handler(commands=["adduser"])
def add_user(message):
    if not is_owner(message.from_user.id):
        return

    try:
        uid = int(message.text.split()[1])
    except:
        bot.send_message(message.chat.id, "❌ Usage: /adduser <id>")
        return

    if uid not in registered_users:
        registered_users.append(uid)
        update_script()

    bot.send_message(message.chat.id, f"✅ User {uid} added.")


@bot.message_handler(commands=["removeuser"])
def remove_user(message):
    if not is_owner(message.from_user.id):
        return

    try:
        uid = int(message.text.split()[1])
    except:
        bot.send_message(message.chat.id, "❌ Usage: /removeuser <id>")
        return

    if uid in registered_users and uid != OWNER_ID:
        registered_users.remove(uid)
        update_script()

    bot.send_message(message.chat.id, f"🗑 Removed {uid}")


@bot.message_handler(commands=["listusers"])
def list_users(message):
    if not is_owner(message.from_user.id):
        return

    text = "📜 <b>Registered Users</b>\n\n"
    for uid in registered_users:
        text += f"🆔 {uid}\n"

    bot.send_message(message.chat.id, text)


# =====================================================
#  GROUP LOCK SYSTEM
# =====================================================

def unlock_group(chat_id):
    bot.send_message(chat_id, "🔓 Group unlocked!")

    try:
        bot.set_chat_permissions(chat_id, types.ChatPermissions(can_send_messages=True))
    except:
        pass


@bot.message_handler(commands=["settime"])
def lock_group(message):
    if not is_owner(message.from_user.id):
        return

    try:
        duration = message.text.split()[1]
    except:
        bot.send_message(message.chat.id, "❌ Usage: /settime <10m|1h|2h>")
        return

    value = int(duration[:-1])
    unit = duration[-1]

    seconds = value * 60 if unit == "m" else value * 3600

    bot.send_message(message.chat.id, f"🔒 Group locked for {duration}")

    try:
        bot.set_chat_permissions(message.chat.id, types.ChatPermissions(can_send_messages=False))
    except:
        pass

    threading.Timer(seconds, unlock_group, args=[message.chat.id]).start()


# =====================================================
#  START
# =====================================================

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "🤖 Security Bot Activated.")


# =====================================================
#  RUN BOT
# =====================================================

bot.infinity_polling()
