# Telegram-Keyword-Alert-Bot
This Python script is a Telegram bot that alerts you when a keyword is mentioned from one or more channel(s).

## Features
**Keyword Detection**: It check each new message for specific keywords in one or more channel(s). If a keyword is mentioned, it sends a message to a you with the keyword and a link to the message.

**System Status**: It can provide system status information when requested with the `/status` command. If a service name is provided with the command, it sends the status of that service. Otherwise, it sends general system information.

**Message Counts**: It can provide the message counts for each channel when requested with the `/counts` command.

**Message Deletion**: Every command and it's output will be deleted after 30 seconds.

## Setup
You should fill every keys in `config.yml` here are explanations:

`api_id`: Your Telegram API ID.  
`api_hash`: Your Telegram API hash.  
`bot_token`: The token for your Telegram bot.  
`user_id`: The ID of the user to send keyword notifications to.  
`channel_id`: A list of channel ID to monitor.  
`keywords`: A list of keywords to check for in messages.  


## Install dependencies
```bash
cd Telegram-Keyword-Alert-Bot
poetry install
```
## Run
```bash
poetry run python3 main.py
```

## Thanks
[Github Copilot](https://copilot.github.com/) for helping me write this bot.
