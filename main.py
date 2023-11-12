import asyncio
from telethon import TelegramClient, events
import telebot
import logging
import os
from datetime import timedelta
import yaml
import threading
import time
from commands import status
from commands import counts
from commands import service_status

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the configuration from the YAML file
try:
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
except Exception as e:
    logging.error(f"An error occurred while loading the configuration: {e}")
    config = {}

try:
    client = TelegramClient('anon', config['api_id'], config['api_hash'])
    bot = telebot.TeleBot(config['bot_token'])
except Exception as e:
    logging.error(f"An error occurred while initializing the Telegram client or bot: {e}")

# Constants
TELEGRAM_LINK_PREFIX = "https://t.me/c/"

class MessageCounter:
    def __init__(self):
        self.counter = {}
        self.start_time = time.time()

    def increment(self, channel_title, channel_link):
        if channel_title not in self.counter:
            self.counter[channel_title] = {'count': 0, 'link': channel_link}
        self.counter[channel_title]['count'] += 1

    def get_counts(self):
        return self.counter

    def get_uptime(self):
        uptime_seconds = time.time() - self.start_time
        return str(timedelta(seconds=int(uptime_seconds)))

message_counter = MessageCounter()

# Register an event handler for each channel
for channel_link in config.get('channel_links', []):
    @client.on(events.NewMessage(chats=channel_link))
    async def handle_new_message_event(event):
        try:
            # Get the channel's information
            channel = await event.get_chat()
            message_counter.increment(channel.title, channel_link)
            for keyword in config.get('keywords', []):
                if keyword in event.raw_text:
                    logging.info("Keyword found in message. Sending message...")
                    message_link = f"{TELEGRAM_LINK_PREFIX}{channel_link}/{event.id}"
                    bot.send_message(config['user_id'], f"关键词: {keyword}\n链接: {message_link}")
        except Exception as e:
            logging.error(f"An error occurred while handling a new message event: {e}")

@bot.message_handler(commands=['status'])
def handle_status_command(message):
    # Split the message text into words
    words = message.text.split()
    # If there is a second word, use it as the service name
    if len(words) > 1:
        service_name = words[1]
        service_status.send_service_status(bot, message, service_name)
    else:
        status.send_system_info(bot, message, message_counter)

@bot.message_handler(commands=['counts'])
def send_message_counts(message):
    counts.send_message_counts(bot, message, message_counter)

def start_polling():
    try:
        bot.polling()
    except Exception as e:
        logging.error(f"An error occurred while starting bot polling: {e}")

async def main():
    try:
        logging.info("Starting client...")
        await client.start()
        logging.info("Client started. Running until disconnected...")
        threading.Thread(target=start_polling).start()  # Start polling in a new thread
        await client.run_until_disconnected()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("Stopping bot polling...")
        bot.stop_polling()
        logging.info("Logging out...")
        await client.log_out()
        logging.info("Logged out.")

# Run the main function
try:
    asyncio.run(main())
except Exception as e:
    logging.error(f"An error occurred while running the main function: {e}")