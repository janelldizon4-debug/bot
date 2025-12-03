import telebot
from telebot import types
import json
import os
import random
import threading
import time
import requests
import io

BOT_TOKEN = "8389171340:AAGflq0Tzt2hmT0AZvKLD859Rw9IPOFggmw"
bot = telebot.TeleBot(BOT_TOKEN)

WELCOME_FILE = "welcome_messages.json"
OWNER_ID = 6784382795
ACCESS_KEY = "Cris-rank-2025"

# ===================== #
#  AUTO DELETE SYSTEM   #
# ===================== #
AUTO_DELETE_DELAY = 1800  # 30 minutes (in seconds)

def auto_delete(chat_id, message_id):
    """Deletes a bot message silently after delay."""
    time.sleep(AUTO_DELETE_DELAY)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass  # ignore errors (e.g., message already deleted)

def send_and_auto_delete(chat_id, *args, **kwargs):
    """Send message and schedule deletion if private chat."""
    msg = bot.send_message(chat_id, *args, **kwargs)
    try:
        chat = bot.get_chat(chat_id)
        if chat.type == "private":  # only delete private chat messages
            threading.Thread(target=auto_delete, args=(chat_id, msg.message_id), daemon=True).start()
    except:
        pass
    return msg
     

# ===================== #
#   WELCOME FILE LOAD   #
# ===================== #
if not os.path.exists(WELCOME_FILE):
    with open(WELCOME_FILE, "w") as f:
        json.dump({}, f, indent=4)

def load_welcome():
    with open(WELCOME_FILE, "r") as f:
        return json.load(f)

def save_welcome(data):
    with open(WELCOME_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===================== #
#     ADMIN CHECK       #
# ===================== #
def is_admin_or_owner(chat_id, user_id):
    if user_id == OWNER_ID:
        return True
    try:
        admins = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
        return user_id in admins
    except:
        return False
        
        # ===================== #
#   BALANCE CHECK DECORATOR
# ===================== #
def require_balance(func):
    """Decorator to block commands if user has no balance."""
    def wrapper(message, *args, **kwargs):
        bal = user_balance.get(message.from_user.id, 0)
        if bal <= 0:
            send_and_auto_delete(message.chat.id, "❌ Access denied. You have no balance.")
            return
        return func(message, *args, **kwargs)
    return wrapper
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user

    # Fancy Crisbot start text
    text = (
        f"────「 𝙲𝚁𝙸𝚂𝙱𝙾𝚃 」────\n"
        f"❂ ʜᴇʟʟ𝚘 {user.first_name}.{user.id}...\n"
        f"×⋆✦⋆──────────────⋆✦⋆×\n"
        f"ɪ ᴀᴍ 𝙲𝚛𝚒𝚜𝚋𝚘𝚝 ᴀ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴡʜɪᴄʜ ᴄᴀɴ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀɴᴅ ꜱᴇᴄᴜʀᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ.\n"
        f"×⋆✦⋆──────────────⋆✦⋆×\n"
        f"ᴄʟɪᴄᴋ ᴏɴ /help ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ!"
    )

    # Inline button to add bot to a group
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "➕ Add me to your group", 
            url=f"https://t.me/{bot.get_me().username}?startgroup=true"
        )
    )

    # Welcome image
    start_image = "https://i.ibb.co/Z7SvBv0/Picsart-25-10-29-09-31-06-902.jpg"

    # Send photo with caption and inline button
    bot.send_photo(
        chat_id=message.chat.id, 
        photo=start_image, 
        caption=text, 
        parse_mode="Markdown", 
        reply_markup=markup
    )

# ===================== #
#       MENU COMMAND
# ===================== #

        
    

# --- Command Handler ---
@bot.message_handler(commands=['html'])
def choose_celebration(message):
    if message.chat.type in ['group', 'supergroup']:
        bot.reply_to(
            message,
            f"⚠️ This command only works in *private chat*.\n"
            f"👉 [Click here to message me privately](t.me/{bot.get_me().username})",
            parse_mode="Markdown"
        )
        return

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Birthday", "Graduation", "Wedding", "Surprise 🎁","Valentine's Day ❤️")
    sent = bot.send_message(message.chat.id, "🎉 Choose the celebration type:", reply_markup=markup)
    schedule_delete(message.chat.id, sent.message_id)
    bot.register_next_step_handler(sent, ask_details_by_type)

def ask_details_by_type(message):
    celebration_type = message.text.strip().lower()

    if celebration_type == "birthday":
        sent = bot.send_message(message.chat.id, "🎂 Enter the *name* of the birthday celebrant:", parse_mode="Markdown")
        bot.register_next_step_handler(sent, ask_birthday_date)

    elif celebration_type == "graduation":
        sent = bot.send_message(message.chat.id, "🎓 Enter the *name* of the graduate:", parse_mode="Markdown")
        bot.register_next_step_handler(sent, ask_graduation_date)

    elif celebration_type == "wedding":
        sent = bot.send_message(message.chat.id, "💍 Enter the *name(s) of the couple*:", parse_mode="Markdown")
        bot.register_next_step_handler(sent, ask_wedding_date)

    elif celebration_type in ["surprise 🎁", "surprise"]:
        sent = bot.send_message(message.chat.id, "🎉 Let's make a Surprise card! First, enter the *recipient's name*:", parse_mode="Markdown")
        bot.register_next_step_handler(sent, ask_surprise_name)
        
    elif celebration_type in ["valentine's day ❤️", "valentine's day"]:
        sent = bot.send_message(message.chat.id, "❤️ Enter the *name* of your Valentine:", parse_mode="Markdown")
        bot.register_next_step_handler(sent, ask_valentine_name)

    else:
        sent = bot.send_message(message.chat.id, "❌ Invalid choice. Please type /html to try again.")
        schedule_delete(message.chat.id, sent.message_id)
        
        # --- VALENTINE'S FLOW ---
def ask_valentine_name(message):
    sent = bot.send_message(
        message.chat.id,
        "💖 Enter your partner's name for the Valentine's card:",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, ask_valentine_callsign)

def ask_valentine_callsign(message):
    name = message.text.strip()
    sent = bot.send_message(
        message.chat.id,
        f"💞 What do you call {name}? (Nickname or callsign)",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, ask_valentine_since, name)

def ask_valentine_since(message, name):
    callsign = message.text.strip()
    sent = bot.send_message(
        message.chat.id,
        f"📅 Since when have you been together? (format: YYYY-MM-DD)",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, ask_valentine_relationship, name, callsign)

def ask_valentine_relationship(message, name, callsign):
    since_date = message.text.strip()
    sent = bot.send_message(
        message.chat.id,
        "💞 Enter your relationship type (e.g., couple, lovebirds, fiancés):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, ask_valentine_logo, name, callsign, since_date)

def ask_valentine_logo(message, name, callsign, since_date):
    relationship = message.text.strip()
    sent = bot.send_message(
        message.chat.id,
        f"📸 Upload or send the image/logo URL for {name}'s Valentine card (jpg/png). "
        "You can host your image here: https://host-image-puce.vercel.app/\n"
        "Or just type 'none' if you don't want a logo.",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, ask_valentine_message, name, callsign, since_date, relationship)

def ask_valentine_message(message, name, callsign, since_date, relationship):
    logo_url = message.text.strip()
    if logo_url.lower() == "none":
        logo_url = ""
    sent = bot.send_message(
        message.chat.id,
        f"💌 Enter your Valentine message for {name}:",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, ask_valentine_sender, name, callsign, since_date, relationship, logo_url)

def ask_valentine_sender(message, name, callsign, since_date, relationship, logo_url):
    msg_text = message.text.strip()
    sent = bot.send_message(
        message.chat.id,
        "✍️ Who is sending this Valentine card? (Enter your name)",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, generate_valentine_html, name, callsign, since_date, relationship, logo_url, msg_text)

def generate_valentine_html(message, name, callsign, since_date, relationship, logo_url, msg_text):
    sender_name = message.text.strip()

    from datetime import datetime
    try:
        since = datetime.strptime(since_date, "%Y-%m-%d")
        years = datetime.now().year - since.year - ((datetime.now().month, datetime.now().day) < (since.month, since.day))
    except Exception:
        years = "N/A"

    background_url = "https://i.ibb.co/Z66JFKBj/images-4.jpg"

    html_code = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>Happy Valentine's {name}!</title>
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&display=swap" rel="stylesheet">
<style>
@keyframes rainbow {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
body {{
    font-family: 'Dancing Script', cursive;
    background: url('{background_url}') no-repeat center center fixed;
    background-size: cover;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; margin: 0;
}}
.container {{
    background: rgba(255,255,255,0.85);
    padding: 50px 30px;
    border-radius: 20px;
    text-align: center;
    max-width: 800px;
    width: 90%;
    border: 5px solid;
    border-image: linear-gradient(45deg, red, pink, purple) 1;
}}
img {{
    width: 180px;
    height: 180px;
    border-radius: 50%;
    object-fit: cover;
    border: 5px solid #ff69b4;
    margin-bottom: 20px;
}}
h1 {{
    font-size: clamp(24px, 6vw, 100px);
    margin-bottom: 20px;
    background: linear-gradient(270deg, red, pink, purple, violet);
    background-size: 1400% 1400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: rainbow 10s ease infinite;
}}
.message-box {{
    background: #ffe4e1;
    padding: 30px 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    font-size: clamp(20px, 4vw, 80px);
    word-wrap: break-word;
}}
.from {{
    font-style: italic;
    font-size: clamp(18px, 3vw, 60px);
}}
p.info {{ margin:10px 0; font-size: clamp(20px,3vw,60px); }}
</style>
</head>
<body>
<div class="container">
    {'<img src="'+logo_url+'" alt="Logo" class="img">' if logo_url else ''}
    <h1>❤️ Happy Valentine's, {name}!</h1>
    <p class="info">Callsign: {callsign}</p>
    <p class="info">Relationship: {relationship}</p>
    <p class="info">Years Together: {years}</p>
    <div class="message-box"><p>{msg_text}</p></div>
    <p class="from">From: {sender_name}</p>
</div>
</body>
</html>"""

    send_html_file(message.chat.id, html_code, f"Valentine_{name}")

# --- SURPRISE FLOW ---
def ask_surprise_name(message):
    sent = bot.send_message(message.chat.id, "🎉 Enter the recipient's name for the surprise card:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_surprise_logo)

def ask_surprise_logo(message):
    name = message.text.strip()
    title = "I have a little surprise for you"  # default title
    sent = bot.send_message(
        message.chat.id,
        f"📸 Upload or send the image/logo URL for {name}'s surprise card (jpg/png). "
        "You can host your image here: https://host-image-puce.vercel.app/",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, ask_surprise_message, name, title)

def ask_surprise_message(message, name, title):
    logo_url = message.text.strip()
    sent = bot.send_message(message.chat.id, f"💌 Enter the surprise message for {name}:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_surprise_sender, name, title, logo_url)

def ask_surprise_sender(message, name, title, logo_url):
    msg_text = message.text.strip()
    sent = bot.send_message(message.chat.id, f"✍️ Who is sending this surprise? Enter your name:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, generate_surprise_html, name, title, logo_url, msg_text)

def generate_surprise_html(message, name, title, logo_url, msg_text):
    sender_name = message.text.strip()
    background_url = "https://i.ibb.co/BHpFv6Tq/images-2.jpg"  # birthday-style background

    html_code = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>🎁 Surprise for {name}!</title>
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&display=swap" rel="stylesheet">
<style>
@keyframes rainbow {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
body {{
    font-family: 'Dancing Script', cursive;
    background: url('{background_url}') no-repeat center center fixed;
    background-size: cover;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; margin: 0;
}}
.container {{
    background: rgba(255,255,255,0.85);
    padding: 50px 30px;
    border-radius: 20px;
    text-align: center;
    max-width: 800px;
    width: 90%;
    border: 5px solid;
    border-image: linear-gradient(45deg, red, green, blue) 1;
}}
img {{
    width: 180px;
    height: 180px;
    border-radius: 50%;
    object-fit: cover;
    border: 5px solid #ff69b4;
    margin-bottom: 20px;
}}
h1 {{
    font-size: clamp(24px, 6vw, 100px);
    margin-bottom: 20px;
    background: linear-gradient(270deg, red, orange, yellow, green, blue, indigo, violet);
    background-size: 1400% 1400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: rainbow 10s ease infinite;
}}
.message-box {{
    background: #ffe4e1;
    padding: 30px 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    font-size: clamp(20px, 4vw, 80px);
    word-wrap: break-word;
}}
.from {{
    font-style: italic;
    font-size: clamp(18px, 3vw, 60px);
}}
</style>
</head>
<body>
<div class="container">
    <img src="{logo_url}" alt="Logo" class="logo">
    <h1>🎉 {title}, {name}!</h1>
    <div class="message-box"><p>{msg_text}</p></div>
    <p class="from">From: {sender_name}</p>
</div>
</body>
</html>"""

    send_html_file(message.chat.id, html_code, f"Surprise_{name}")


# --- Birthday Flow ---
def ask_birthday_date(message):
    name = message.text.strip()
    sent = bot.send_message(message.chat.id, f"📅 Enter {name}'s birthday (YYYY-MM-DD):", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_birthday_age, name)

def ask_birthday_age(message, name):
    birthdate = message.text.strip()
    sent = bot.send_message(message.chat.id, f"🎈 Enter the age {name} will turn:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_birthday_relation, name, birthdate)

def ask_birthday_relation(message, name, birthdate):
    age = message.text.strip()
    sent = bot.send_message(message.chat.id, f"❤️ What is your relation to {name}?", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_birthday_sender_name, name, birthdate, age)

def ask_birthday_sender_name(message, name, birthdate, age):
    relation = message.text.strip()
    sent = bot.send_message(message.chat.id, f"📝 Enter your name (the sender) for {name}'s birthday gift card:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_birthday_image, name, birthdate, age, relation)

def ask_birthday_image(message, name, birthdate, age, relation):
    sender_name = message.text.strip()
    sent = bot.send_message(
        message.chat.id,
        "📸 Upload or send the image link of the celebrant (jpg/png). "
        "You can host your image here: https://host-image-puce.vercel.app/",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, ask_birthday_message, name, birthdate, age, relation, sender_name)

def ask_birthday_message(message, name, birthdate, age, relation, sender_name):
    image_url = message.text.strip()
    sent = bot.send_message(message.chat.id, f"💌 Enter your birthday message for {name}:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, generate_birthday_html, name, birthdate, age, relation, sender_name, image_url)

def generate_birthday_html(message, name, birthdate, age, relation, sender_name, image_url):
    msg_text = message.text.strip()
    html_code = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>🎉 {name}'s Birthday!</title>
<!-- Google Cursive Font -->
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&display=swap" rel="stylesheet">
<style>
body {{
    font-family: 'Dancing Script', cursive;
    background: url('https://i.ibb.co/BHpFv6Tq/images-2.jpg') no-repeat center center fixed;
    background-size: cover;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; margin: 0;
}}

.container {{
    background: rgba(255,255,255,0.85);
    padding: 50px 30px;       
    border-radius: 20px;
    text-align: center;
    max-width: 800px;         
    width: 90%;
    border: 5px solid;
    border-image: linear-gradient(45deg, red, green, blue) 1;
}}

img {{
    width: 180px;
    height: 180px;
    border-radius: 50%;
    object-fit: cover;
    border: 5px solid #ff69b4;
    margin-bottom: 20px;
}}

h1 {{
    font-size: clamp(24px, 6vw, 100px);
    margin-bottom: 20px;
}}

.details {{
    margin-bottom: 20px;
    font-size: clamp(18px, 3vw, 60px);
}}

.message-box {{
    background: #ffe4e1;
    padding: 30px 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    font-size: clamp(20px, 4vw, 80px);
    word-wrap: break-word;
}}

.from {{
    font-style: italic;
    font-size: clamp(18px, 3vw, 60px);
}}
</style>
</head>
<body>
<div class="container">
    <img src="{image_url}" alt="{name}" loading="lazy">
    <h1>🎉 Happy Birthday, {name}!</h1>
    <div class="details">
        <p>For: {name}</p>
        <p>Birthdate: {birthdate}</p>
        <p>Age Turning: {age}</p>
        <p>Relation: {relation}</p>
    </div>
    <div class="message-box"><p>{msg_text}</p></div>
    <p class="from">From: {sender_name} ({relation})</p>
</div>
</body>
</html>"""
    send_html_file(message.chat.id, html_code, name)


# --- Graduation Flow ---
def ask_graduation_date(message):
    name = message.text.strip()
    sent = bot.send_message(message.chat.id, f"📅 Enter the graduation date for {name} (YYYY-MM-DD):", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_graduation_relation, name)

def ask_graduation_relation(message, name):
    grad_date = message.text.strip()
    sent = bot.send_message(message.chat.id, f"❤️ What is your relation to {name}?", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_graduation_sender_name, name, grad_date)

def ask_graduation_sender_name(message, name, grad_date):
    relation = message.text.strip()
    sent = bot.send_message(message.chat.id, f"📝 Enter your name (the sender) for {name}'s graduation gift card:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_graduation_image, name, grad_date, relation)

def ask_graduation_image(message, name, grad_date, relation):
    sender_name = message.text.strip()
    sent = bot.send_message(
        message.chat.id,
        "📸 Upload or send the image link of the graduate (jpg/png). "
        "You can host your image here: https://host-image-puce.vercel.app/",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, ask_graduation_message, name, grad_date, relation, sender_name)

def ask_graduation_message(message, name, grad_date, relation, sender_name):
    image_url = message.text.strip()
    sent = bot.send_message(message.chat.id, f"💌 Enter your congratulatory message for {name}:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, generate_graduation_html, name, grad_date, image_url, relation, sender_name)
    
def generate_graduation_html(message, name, grad_date, image_url, relation, sender_name):
    msg_text = message.text.strip()
    html_code = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>🎓 {name}'s Graduation!</title>
<!-- Google Cursive Font -->
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&display=swap" rel="stylesheet">
<style>
body {{
    font-family: 'Dancing Script', cursive;
    background: url('https://i.ibb.co/rfvTqWgR/images-3.jpg') no-repeat center center fixed;
    background-size: cover;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; margin: 0;
}}

.container {{
    background: rgba(255,255,255,0.85);
    padding: 50px 30px;         
    border-radius: 20px;
    text-align: center;
    max-width: 800px;
    width: 90%;
    border: 5px solid;
    border-image: linear-gradient(45deg, red, green, blue) 1;
}}

img {{
    width: 180px;
    height: 180px;
    border-radius: 50%;
    object-fit: cover;
    border: 5px solid #00aaff;
    margin-bottom: 20px;
}}

h1 {{
    font-size: clamp(24px, 6vw, 100px);
    margin-bottom: 20px;
}}

.details {{
    margin-bottom: 20px;
    font-size: clamp(18px, 3vw, 60px);
}}

.message-box {{
    background: #d1f0ff;
    padding: 30px 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    font-size: clamp(20px, 4vw, 80px);
    word-wrap: break-word;
}}

.from {{
    font-style: italic;
    font-size: clamp(18px, 3vw, 60px);
}}
</style>
</head>
<body>
<div class="container">
    <img src="{image_url}" alt="{name}" loading="lazy">
    <h1>🎓 Happy Graduation Day, {name}!</h1>
    <div class="details">
        <p>Graduate: {name}</p>
        <p>Graduation Date: {grad_date}</p>
    </div>
    <div class="message-box"><p>{msg_text}</p></div>
    <p class="from">From: {sender_name} ({relation})</p>
</div>
</body>
</html>"""
    send_html_file(message.chat.id, html_code, name)


# --- Wedding Flow ---
def ask_wedding_date(message):
    couple_name = message.text.strip()
    sent = bot.send_message(message.chat.id, f"📅 Enter the wedding date for {couple_name} (YYYY-MM-DD):", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_wedding_relation, couple_name)

def ask_wedding_relation(message, couple_name):
    wedding_date = message.text.strip()
    sent = bot.send_message(message.chat.id, f"❤️ What is your relation to {couple_name}?", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_wedding_sender_name, couple_name, wedding_date)

def ask_wedding_sender_name(message, couple_name, wedding_date):
    relation = message.text.strip()
    sent = bot.send_message(message.chat.id, f"📝 Enter your name (the sender) for {couple_name}'s gift card:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, ask_wedding_image, couple_name, wedding_date, relation)

def ask_wedding_image(message, couple_name, wedding_date, relation):
    sender_name = message.text.strip()
    sent = bot.send_message(
        message.chat.id,
        "📸 Upload or send the image link of the couple (jpg/png). "
        "You can host your image here: https://host-image-puce.vercel.app/",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, ask_wedding_message, couple_name, wedding_date, relation, sender_name)

def ask_wedding_message(message, couple_name, wedding_date, relation, sender_name):
    image_url = message.text.strip()
    sent = bot.send_message(message.chat.id, f"💌 Enter your wedding message for {couple_name}:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, generate_wedding_html, couple_name, wedding_date, image_url, relation, sender_name)

def generate_wedding_html(message, couple_name, wedding_date, image_url, relation, sender_name):
    msg_text = message.text.strip()
    html_code = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>💍 {couple_name}'s Wedding!</title>
<!-- Google Cursive Font -->
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&display=swap" rel="stylesheet">
<style>
body {{
    font-family: 'Dancing Script', cursive;
    background: url('https://i.ibb.co/BHpFv6Tq/images-2.jpg') no-repeat center center fixed;
    background-size: cover;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; margin: 0;
}}

.container {{
    background: rgba(255,255,255,0.85);
    padding: 50px 30px;      
    border-radius: 20px;
    text-align: center;
    max-width: 800px;         
    width: 90%;
    border: 5px solid;
    border-image: linear-gradient(45deg, red, green, blue) 1;
}}

img {{
    width: 180px;
    height: 180px;
    border-radius: 50%;
    object-fit: cover;
    border: 5px solid #ff8800;
    margin-bottom: 20px;
}}

h1 {{
    font-size: clamp(24px, 6vw, 100px);
    margin-bottom: 20px;
}}

.details {{
    margin-bottom: 20px;
    font-size: clamp(18px, 3vw, 60px);
}}

.message-box {{
    background: #fff2cc;
    padding: 30px 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    font-size: clamp(20px, 4vw, 80px);
    word-wrap: break-word;
}}

.from {{
    font-style: italic;
    font-size: clamp(18px, 3vw, 60px);
}}
</style>
</head>
<body>
<div class="container">
    <img src="{image_url}" alt="{couple_name}" loading="lazy">
    <h1>💍 Happy Wedding Day, {couple_name}!</h1>
    <div class="details">
        <p>Couple: {couple_name}</p>
        <p>Wedding Date: {wedding_date}</p>
    </div>
    <div class="message-box"><p>{msg_text}</p></div>
    <p class="from">From: {sender_name} ({relation})</p>
</div>
</body>
</html>"""
    send_html_file(message.chat.id, html_code, couple_name)


# --- Helper to send HTML file with auto-delete ---
def send_html_file(chat_id, html_code, name):
    file_obj = io.BytesIO(html_code.encode('utf-8'))
    file_obj.name = f"giftcard_{name.lower().replace(' ', '_')}.html"
    sent = bot.send_document(chat_id, file_obj, caption=f"🎁 Gift card for {name}")
    schedule_delete(chat_id, sent.message_id)

# --- Auto-delete after 1 hour ---
def schedule_delete(chat_id, message_id):
    def delete_later():
        time.sleep(3600)
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
    threading.Thread(target=delete_later).start()





    

# ===================== #
#   ADMIN COMMANDS      #
# ===================== #
def extract_user(message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    args = message.text.split()
    if len(args) >= 2 and args[1].isdigit():
        return type('User', (), {'id': int(args[1]), 'first_name': f'User {args[1]}'})()
    return None

@bot.message_handler(commands=['kick'])
def kick_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return send_and_auto_delete(message.chat.id, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return send_and_auto_delete(message.chat.id, "⚠️ Reply or use /kick <user_id>")
    try:
        bot.kick_chat_member(message.chat.id, target.id)
        send_and_auto_delete(message.chat.id, f"👢 {target.first_name} has been kicked!")
    except:
        send_and_auto_delete(message.chat.id, "❌ Failed to kick user.")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return send_and_auto_delete(message.chat.id, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return send_and_auto_delete(message.chat.id, "⚠️ Reply or use /ban <user_id>")
    try:
        bot.ban_chat_member(message.chat.id, target.id)
        send_and_auto_delete(message.chat.id, f"🔒 {target.first_name} has been banned!")
    except:
        send_and_auto_delete(message.chat.id, "❌ Failed to ban user.")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return send_and_auto_delete(message.chat.id, "🚫 You don’t have permission.")
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return send_and_auto_delete(message.chat.id, "⚠️ Usage: /unban <user_id>")
    user_id = int(args[1])
    try:
        bot.unban_chat_member(message.chat.id, user_id)
        send_and_auto_delete(message.chat.id, f"✅ User `{user_id}` has been unbanned!", parse_mode="Markdown")
    except:
        send_and_auto_delete(message.chat.id, "❌ Failed to unban user.")

# ===================== #
#   WARN SYSTEM         #
# ===================== #
user_warnings = {}

@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return send_and_auto_delete(message.chat.id, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return send_and_auto_delete(message.chat.id, "⚠️ Reply or use /warn <user_id>")
    user_warnings[target.id] = user_warnings.get(target.id, 0) + 1
    send_and_auto_delete(message.chat.id, f"⚠️ {target.first_name} has been warned ({user_warnings[target.id]} warnings).")
    if user_warnings[target.id] >= 3:
        bot.kick_chat_member(message.chat.id, target.id)
        bot.send_message(message.chat.id, f"🚨 {target.first_name} reached 3 warnings and was kicked.")
        
# 🔇 Mute Command 
@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.chat.type not in ['group', 'supergroup']:
        return bot.reply_to(message, "This command only works in groups.")
    
    if not message.reply_to_message:
        return bot.reply_to(message, "Reply to a user's message to mute them.")
    
    user_id = message.reply_to_message.from_user.id
    member = bot.get_chat_member(message.chat.id, message.from_user.id)
    
    if member.status not in ['administrator', 'creator']:
        return bot.reply_to(message, "Only admins can mute users.")
    
    until_date = int(time.time() + 3600)  # 1 hour in UTC timestamp
    
    bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=user_id,
        permissions=types.ChatPermissions(can_send_messages=False),
        until_date=until_date
    )
    
    bot.reply_to(
        message,
        f"🔇 User [{user_id}](tg://user?id={user_id}) has been muted for 1 hour ⏳",
        parse_mode="Markdown"
    )


# 🔊 Unmute Command
@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "This command only works in groups.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "Reply to a user's message to unmute them.")
        return

    user_id = message.reply_to_message.from_user.id
    member = bot.get_chat_member(message.chat.id, message.from_user.id)

    # Check if admin
    if member.status not in ['administrator', 'creator']:
        bot.reply_to(message, "Only admins can unmute users.")
        return

    # Restore full permissions
    bot.restrict_chat_member(
        message.chat.id,
        user_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )

    bot.reply_to(message, f"🔊 User [{user_id}](tg://user?id={user_id}) has been unmuted.", parse_mode="Markdown")

@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return send_and_auto_delete(message.chat.id, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return send_and_auto_delete(message.chat.id, "⚠️ Reply or use /unwarn <user_id>")
    user_warnings[target.id] = max(0, user_warnings.get(target.id, 0) - 1)
    send_and_auto_delete(message.chat.id, f"✅ {target.first_name}'s warning removed ({user_warnings[target.id]} left).")

# ===================== #
#   BASIC COMMANDS      #
# ===================== #
@bot.message_handler(commands=['start'])
def start(message):
    send_and_auto_delete(message.chat.id, f"👋 Hello {message.from_user.first_name}!\nWelcome to **Cris Bot** — your King Rank assistant.\nUse /help to see commands.", parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = (
        "🤖 **Cris Bot Command List**\n\n"
        "🛡 **Admin:** /kick /ban /unban /warn /unwarn/mute/unmute\n"
        "💰 **Balance:** /give /balance /menu\n"
        "🧠 **Info:** /id /info /rules /quote\n"
        "🎮 **Fun:** /hug /slap/html"
    )
    send_and_auto_delete(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['id'])
def get_id(message):
    send_and_auto_delete(message.chat.id, f"🆔 Your ID: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def info(message):
    # Determine target user
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    username = f"@{target.username}" if target.username else "❌ No username"
    
    # Get chat member info (to check rank)
    rank = "❌ Unknown"
    try:
        member = bot.get_chat_member(message.chat.id, target.id)
        status = member.status  # can be 'creator', 'administrator', 'member', 'restricted', 'left', 'kicked'
        if status == 'creator':
            rank = "👑 Owner"
        elif status == 'administrator':
            rank = "🛡️ Admin"
        elif status == 'member':
            rank = "👤 Member"
        elif status == 'restricted':
            rank = "⛔ Restricted"
        elif status == 'left':
            rank = "👋 Left"
        elif status == 'kicked':
            rank = "🚫 Banned"
        else:
            rank = f"ℹ️ {status}"
    except:
        rank = "❌ Unknown"

    # Profile link
    profile_link = f"[Link](tg://user?id={target.id})"

    # Send info message
    text = (
        f"👤 Name       : {target.first_name}\n"
        f"💬 Username   : {username}\n"
        f"🆔 Telegram ID: `{target.id}`\n"
        f"🏷️ Rank       : {rank}\n"
        f"🔗 Profile    : {profile_link}"
    )
    send_and_auto_delete(message.chat.id, text, parse_mode="Markdown")
    
# ===================== #
#   FUN COMMANDS        #
# ===================== #
@bot.message_handler(commands=['hug'])
def hug(message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else "everyone"
    send_and_auto_delete(message.chat.id, f"🤗 {message.from_user.first_name} hugged {target}! 💞")

@bot.message_handler(commands=['slap'])
def slap(message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else "someone"
    send_and_auto_delete(message.chat.id, f"👋 {message.from_user.first_name} slapped {target}! 😆")

@bot.message_handler(commands=['quote'])
def quote(message):
    quotes = [
        "🔥 Greatness begins with a single step.",
        "⚔️ Legends aren’t born, they’re made.",
        "🏆 Stay sharp, stay focused, stay king.",
        "🎮 Every loss is just training for your next win."
    ]
    send_and_auto_delete(message.chat.id, random.choice(quotes))

@bot.message_handler(commands=['rules'])
def rules(message):
    send_and_auto_delete(message.chat.id, "📜 **Rules:**\n1️⃣ Respect all\n2️⃣ No spam\n3️⃣ Follow admins\n4️⃣ No NSFW\n5️⃣ Enjoy your stay 👑", parse_mode="Markdown")

# ===================== #
#   WELCOME & GOODBYE   #
# ===================== #
WELCOME_IMAGE = "https://i.ibb.co/Z7SvBv0/Picsart-25-10-29-09-31-06-902.jpg"
GOODBYE_IMAGE = "https://i.ibb.co/pjZjGBvp/Picsart-25-10-28-22-05-21-023.jpg"

import random
import random

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    group_name = message.chat.title

    for member in message.new_chat_members:
        username = f"@{member.username}" if member.username else "❌ None"

        # Professional welcome text
        text = (
            f"🌟 **Welcome to {group_name}!** 🌟\n\n"
            f"👋 Hello, **{member.first_name}**!\n"
            f"💬 Username : {username}\n"
            f"🆔 ID       : `{member.id}`\n\n"
            f"✨ We’re thrilled to have you here. Please check the /rules to get started.\n"
            f"🎮 Enjoy your time and participate actively!\n\n"
            f"📌 Group: **{group_name}**"
        )

        # Optionally, you can use a professional-looking welcome image
        bot.send_photo(
            chat_id=message.chat.id,
            photo=WELCOME_IMAGE,
            caption=text,
            parse_mode="Markdown"
        )
import random

import random

@bot.message_handler(content_types=['left_chat_member'])
def goodbye(message):
    user = message.left_chat_member
    group_name = message.chat.title

    username = f"@{user.username}" if user.username else "❌ None"

    messages = [
        f"😤 **{user.first_name} left {group_name}!**\n\nFinally, less noise. 😒",
        f"👋 **Goodbye, {user.first_name}!**\n\nNobody’s gonna notice anyway 😏",
        f"💨 **{user.first_name} ran away from {group_name}.** Can’t handle the chaos 😂",
        f"🧹 **{user.first_name} disappeared!** The air feels cleaner already 😌",
        f"🚪 **{user.first_name} just left.** Don’t trip over the door on your way out 🤭",
        f"😈 **{user.first_name} left {group_name}.** Peace restored 🫡",
        f"👻 **{user.first_name} vanished.** The group feels lighter 😎",
        f"🕳️ **{user.first_name} is gone!** Maybe they’ll find a quieter place 🙄",
    ]

    text = (
        f"{random.choice(messages)}\n\n"
        f"💬 **Username:** {username}\n"
        f"🆔 `{user.id}`\n"
        f"🏷️ **Group:** {group_name}"
    )

    bot.send_photo(message.chat.id, GOODBYE_IMAGE, caption=text, parse_mode="Markdown")
    

# ===================== AUTO REACTION ===================== 
@bot.message_handler(func=lambda message: True, content_types=['text', 'sticker', 'photo', 'video'])
def auto_react(message):
    if message.from_user.id == bot.get_me().id:
        return

    reactions = [
        "👍", "👀", "🔥", "💯", "✨",
        "😂", "😎", "🤩", "🥳", "💖",
        "🙌", "👏", "😜", "😇", "😏",
        "🤔", "😱", "💪", "🎉", "💥",
        "😢", "😡", "😳", "🥶", "🤯",
        "💤", "🤗", "🤫", "😴", "💫",
        "🫶", "🫡", "🥰", "🫠", "💌",
        "🧿", "🌟", "🍀", "☄️", "💎"
    ]
    emoji = random.choice(reactions)

    # Use Bot API directly to react
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction"
    data = {
        "chat_id": message.chat.id,
        "message_id": message.message_id,
        "reaction": emoji
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Reaction failed: {e}")

# ===================== START BOT LOOP ===================== 
print("✅ Cris Bot is running...")
bot.infinity_polling()
