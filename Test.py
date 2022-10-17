import configparser
import json
import asyncio
import re
from telethon.client import messages
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
from telethon import connection, events, functions
from telethon import functions, types
from array import *

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']
phone = config['Telegram']['phone']
client = TelegramClient(username, 10924741, api_hash)
client.connect()
client.start()

default_currency = config["General"]["default_currency"].split()
print(default_currency)
for mes in client.iter_messages('Test Signals'):
    try:
        result = re.findall(r'\w+', mes.message.upper())
        print(mes.message, result)
    except Exception:
        print("Exception on ", mes)
