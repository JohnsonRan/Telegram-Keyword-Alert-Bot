import asyncio
from telethon import TelegramClient, events
import telebot
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configuration
config = {
    'api_id': 'YOUR_API_ID',  # Replace with your API ID
    'api_hash': 'YOUR_API_HASH',  # Replace with your API hash
    'user_id': YOUR_USER_ID,  # Replace with your user ID
    'keywords': ['test', 'test1'],  # Replace with your keywords
    'channel_link': YOUR_CHANNEL_ID,  # Replace with your channel ID
    'bot_token': 'YOUR_BOT_TOKEN'  # Replace with your bot token
}

client = TelegramClient('anon', config['api_id'], config['api_hash'])
bot = telebot.TeleBot(config['bot_token'])

@client.on(events.NewMessage(chats=config['channel_link']))
async def my_event_handler(event):
    for keyword in config['keywords']:
        if keyword in event.raw_text:
            logging.info("Keyword found in message. Sending message...")
            message_link = f"https://t.me/c/{config['channel_link']}/{event.id}"
            bot.send_message(config['user_id'], f"关键词: {keyword}\n链接: {message_link}")

async def main():
    try:
        logging.info("Starting client...")
        await client.start()
        logging.info("Client started. Running until disconnected...")
        await client.run_until_disconnected()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("Logging out...")
        await client.log_out()
        logging.info("Logged out.")

# Run the main function
asyncio.run(main())