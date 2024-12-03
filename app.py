from flask import Flask, render_template, request, redirect, url_for
import os
import logging
from pyrogram import Client
from pyrogram.errors import UserIsBlocked, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration options (these can be updated)
CONFIG = {
    "bot_username": "REXIESCATBOT",
    "main_channel_url": "https://t.me/mn_movies2",
    "ott_updates_channel_url": "https://t.me/new_ott_movies3",
    "photo_url": "https://i.ibb.co/Q9Hm3Dg/175540848.jpg", 
    "welcome_message": "**{greeting} {name} 👻\n\nWelcome to {chat_name}! Your request has been approved.\n\nSend /start to know more.**",
    "greeting_messages": {
        'en': ['Good Morning', 'Good Afternoon', 'Good Evening'],
        'ru': ['Доброе утро', 'Добрый день', 'Добрый вечер']
    }
}

def get_greeting(language: str):
    """Return a greeting message based on the time of day."""
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting_index = 0  # Good Morning
    elif 12 <= current_hour < 18:
        greeting_index = 1  # Good Afternoon
    else:
        greeting_index = 2  # Good Evening
    
    return CONFIG["greeting_messages"].get(language, CONFIG["greeting_messages"]['en'])[greeting_index]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        bot_token = request.form['bot_token']
        return redirect(url_for('run_bot', token=bot_token))
    return render_template("index.html")

@app.route("/start", methods=["GET", "POST"])
def run_bot():
    """Runs the bot and accepts join requests."""
    if request.method == "POST":
        bot_token = request.form['bot_token']
        try:
            app = Client("my_bot", bot_token=bot_token)

            @app.on_chat_join_request()
            async def accept_request(client, r):
                try:
                    rm = InlineKeyboardMarkup([[
                        InlineKeyboardButton('🎉 Add Me To Your Groups 🎉', url=f'http://t.me/{CONFIG["bot_username"]}?startgroup=true')
                    ], [
                        InlineKeyboardButton('OTT Updates', url=CONFIG["ott_updates_channel_url"]),
                        InlineKeyboardButton('Main Channel', url=CONFIG["main_channel_url"])
                    ]])

                    greeting = get_greeting(r.from_user.language_code or 'en')

                    welcome_text = CONFIG["welcome_message"].format(
                        greeting=greeting, 
                        name=r.from_user.first_name or r.from_user.username,
                        chat_name=r.chat.title
                    )

                    await client.send_photo(r.from_user.id, CONFIG["photo_url"], welcome_text, reply_markup=rm, parse_mode=ParseMode.MARKDOWN)
                    await r.approve()

                    logger.info(f"Processed join request from {r.from_user.username} in {r.chat.title}")
                except UserIsBlocked:
                    logger.warning(f"User {r.from_user.username} has blocked the bot.")
                except PeerIdInvalid:
                    logger.error(f"Invalid Peer ID when processing request for {r.from_user.username}.")
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")

            app.run()
            return f"Bot running with token {bot_token}. Please check your bot!"

        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            return f"Failed to start bot: {str(e)}"
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Ensure Flask listens on all network interfaces and uses the correct port
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

