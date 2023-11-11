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

@client.on(events.NewMessage(chats=config['channel_link']))
async def my_event_handler(event):
    for keyword in config['keywords']:
        if keyword in event.raw_text:
            logging.info("Keyword found in message. Sending message...")
            message_link = f"https://t.me/c/{config['channel_link']}/{event.id}"
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