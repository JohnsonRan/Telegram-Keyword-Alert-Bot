import asyncio
from telethon import TelegramClient, events
import telebot
import logging
import os
from datetime import timedelta
import yaml
import threading
import time
from contextlib import suppress
from functools import partial
from commands import status
from commands import counts
from commands import service_status

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the configuration from the YAML file
with suppress(Exception):
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
config = config or {}

with suppress(Exception):
    client = TelegramClient('anon', config['api_id'], config['api_hash'])
    bot = telebot.TeleBot(config['bot_token'])

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

# A global message counter
message_counter = MessageCounter()

# A list to store the messages to be deleted
messages_to_delete = []

def schedule_message_deletion(command_message, response_message):
    # Add the command message and the bot's response to the list
    messages_to_delete.append((command_message, response_message))

    # Start a new thread to delete the messages if it's not already running
    if not any(thread.is_alive() for thread in threading.enumerate() if thread.name == 'delete_messages_thread'):
        threading.Thread(target=delete_messages, args=(messages_to_delete,), name='delete_messages_thread').start()

# Register an event handler for each channel
for channel_link in config.get('channel_id', []):
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

def delete_messages(messages):
    time.sleep(30)  # Wait for 30 seconds
    logging.info("Messages deleted...")
    
    # Delete the command message and the bot's response
    for message, sent_message in messages:
        with suppress(Exception):
            bot.delete_message(message.chat.id, message.message_id)
            bot.delete_message(sent_message.chat.id, sent_message.message_id)

@bot.message_handler(commands=['status'])
def handle_status_command(message):
    # Split the message text into words
    words = message.text.split()
    # If there is a second word, use it as the service name
    if len(words) > 1:
        service_name = words[1]
        sent_message = service_status.send_service_status(bot, message, service_name)
    else:
        sent_message = status.send_system_info(bot, message, message_counter)

    # Schedule the command message and the bot's response for deletion
    schedule_message_deletion(message, sent_message)

@bot.message_handler(commands=['counts'])
def send_message_counts(message):
    sent_message = counts.send_message_counts(bot, message, message_counter)

    # Schedule the command message and the bot's response for deletion
    schedule_message_deletion(message, sent_message)

def start_polling():
    with suppress(Exception):
        bot.polling()

async def main():
    try:
        logging.info("Starting client...")
        await client.start()
        logging.info("Client started. Running until disconnected...")
        threading.Thread(target=start_polling).start()  # Start polling in a new thread
        await client.run_until_disconnected()
    except Exception:
        logging.exception("An error occurred")
    finally:
        logging.info("Stopping bot polling...")
        bot.stop_polling()
        logging.info("Logging out...")
        await client.log_out()
        logging.info("Logged out.")

# Run the main function
with suppress(Exception):
    asyncio.run(main())