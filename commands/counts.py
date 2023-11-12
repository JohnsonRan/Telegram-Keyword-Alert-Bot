import logging
from telebot import TeleBot

# Constants
TELEGRAM_LINK_PREFIX = "https://t.me/c/"

def send_message_counts(bot: TeleBot, message, message_counter):
    try:
        logging.info("Received /counts command")  # Log a message when the /count command is received

        # Build the message
        counts = message_counter.get_counts()
        msg = "已检查消息数：\n" + "\n".join(f"[{channel_name}]({TELEGRAM_LINK_PREFIX}{info['link']}): {info['count']}" for channel_name, info in counts.items())

        # Send the message
        try:
            sent_message = bot.reply_to(message, msg)
            return sent_message
        except Exception as e:
            logging.error(f"An error occurred while sending message counts: {e}")
    except Exception as e:
        logging.error(f"An error occurred while getting message counts: {e}")