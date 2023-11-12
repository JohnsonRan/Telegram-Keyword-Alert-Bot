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
import time

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
def send_system_info(message):
    try:
        logging.info("Received /status command")  # Log a message when the /check command is received

        # 计算脚本运行时间
        uptime = message_counter.get_uptime()

        # 获取CPU使用情况
        cpu_usage = psutil.cpu_percent(interval=1)

        # 获取内存使用情况
        memory_info = psutil.virtual_memory()
        total_memory_gb = memory_info.total / (1024.0 ** 3)  # Convert bytes to GB
        used_memory_gb = (memory_info.total - memory_info.available) / (1024.0 ** 3)  # Convert bytes to GB

        # 如果内存小于1GB，则以MB的形式显示
        if used_memory_gb < 1:
            used_memory = f"{used_memory_gb * 1024:.2f}MB"
        else:
            used_memory = f"{used_memory_gb:.2f}GB"

        if total_memory_gb < 1:
            total_memory = f"{total_memory_gb * 1024:.2f}MB"
        else:
            total_memory = f"{total_memory_gb:.2f}GB"

        # 获取服务器时间
        server_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 构建消息
        msg = f"运行时间: {uptime}\nCPU使用率: {cpu_usage}%\n内存: {used_memory} / {total_memory}\n服务器时间: {server_time}"

        # 发送消息
        bot.reply_to(message, msg)
    except Exception as e:
        logging.error(f"An error occurred while sending system info: {e}")

@bot.message_handler(commands=['counts'])
def send_message_counts(message):
    try:
        logging.info("Received /counts command")  # Log a message when the /count command is received

        # Build the message
        counts = message_counter.get_counts()
        msg = "已检查消息数：\n" + "\n".join(f"[{channel_name}]({TELEGRAM_LINK_PREFIX}{info['link']}): {info['count']}" for channel_name, info in counts.items())

        # Send the message
        bot.reply_to(message, msg, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"An error occurred while sending message counts: {e}")

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