# commands/service_status.py
import logging
import subprocess
from telebot import TeleBot

def send_service_status(bot: TeleBot, message, service_name):
    logging.info(f"Received /status {service_name} command")
    try:
        # Get the service status
        status_output = subprocess.check_output(["systemctl", "show", "--no-page", service_name], universal_newlines=True)
        status_lines = status_output.split("\n")
        status_info = {line.split("=")[0]: line.split("=")[1] for line in status_lines if "=" in line}
        active_state = status_info.get("ActiveState", "unknown")
        sub_state = status_info.get("SubState", "unknown")
        uptime = status_info.get("ActiveEnterTimestamp", "unknown")

        # Get the last three journal entries
        journal_output = subprocess.check_output(["journalctl", "-u", service_name, "-n", "3", "--no-pager"], universal_newlines=True)
        journal_entries = journal_output.split("\n")

        # Build the message
        msg = f"服务状态:\n\n服务名: {service_name}\n活动状态: {active_state}\n子状态: {sub_state}\n运行时间: {uptime}\n\n最近的日志条目:\n\n```"
        msg += "\n\n".join(journal_entries)
        msg += "```"

        # Send the message and return the sent message
        try:
            sent_message = bot.reply_to(message, msg, parse_mode='Markdown')
            return sent_message
        except Exception as e:
            logging.error(f"An error occurred while sending service status: {e}")
    except Exception as e:
        logging.error(f"An error occurred while getting service status: {e}")