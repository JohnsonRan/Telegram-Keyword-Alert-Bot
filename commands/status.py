import logging
import psutil
from datetime import datetime
from telebot import TeleBot

def send_system_info(bot: TeleBot, message, message_counter):
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
        server_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 构建消息
        msg = f"运行时间: {uptime}\nCPU使用率: {cpu_usage}%\n内存: {used_memory} / {total_memory}\n服务器时间: {server_time}"

        # 发送消息
        try:
            sent_message = bot.reply_to(message, msg)
            return sent_message
        except Exception as e:
            logging.error(f"An error occurred while sending system info: {e}")
    except Exception as e:
        logging.error(f"An error occurred while getting system info: {e}")