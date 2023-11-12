import asyncio
from telethon import TelegramClient, events
import telebot
import logging
import os
import psutil
from datetime import timedelta
import datetime
import subprocess
import yaml
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the configuration from the YAML file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

client = TelegramClient('anon', config['api_id'], config['api_hash'])
bot = telebot.TeleBot(config['bot_token'])

# Constants
TELEGRAM_LINK_PREFIX = "https://t.me/c/"

class MessageCounter:
    def __init__(self):
        self.counter = {}

    def increment(self, channel_title, channel_link):
        if channel_title not in self.counter:
            self.counter[channel_title] = {'count': 0, 'link': channel_link}
        self.counter[channel_title]['count'] += 1

    def get_counts(self):
        return self.counter

message_counter = MessageCounter()

# Register an event handler for each channel
for channel_link in config['channel_links']:
    @client.on(events.NewMessage(chats=channel_link))
    async def handle_new_message(event):
        # Get the channel's information
        channel = await event.get_chat()
        message_counter.increment(channel.title, channel_link)
        for keyword in config['keywords']:
            if keyword in event.raw_text:
                logging.info("Keyword found in message. Sending message...")
                message_link = f"{TELEGRAM_LINK_PREFIX}{channel_link}/{event.id}"
                bot.send_message(config['user_id'], f"关键词: {keyword}\n链接: {message_link}")

@bot.message_handler(commands=['check'])
def send_system_info(message):
    logging.info("Received /check command")  # Log a message when the /check command is received

    # 获取系统运行时间
    uptime = subprocess.check_output(['uptime', '-p']).decode('utf-8').strip()

    # 获取CPU使用情况
    cpu_usage = psutil.cpu_percent(interval=1)

    # 获取内存使用情况
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    # 获取服务器时间
    server_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 构建消息
    msg = f"服务器运行时间: {uptime}\nCPU使用率: {cpu_usage}%\n内存使用率: {memory_usage}%\n服务器时间: {server_time}"

    # 发送消息
    bot.reply_to(message, msg)

@bot.message_handler(commands=['count'])
def send_message_counts(message):
    logging.info("Received /count command")  # Log a message when the /count command is received

    # Build the message
    counts = message_counter.get_counts()
    msg = "已检查消息数：\n" + "\n".join(f"[{channel_name}]({TELEGRAM_LINK_PREFIX}{info['link']}): {info['count']}" for channel_name, info in counts.items())

    # Send the message
    bot.reply_to(message, msg, parse_mode='Markdown')

def start_polling():
    bot.polling()

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
asyncio.run(main())