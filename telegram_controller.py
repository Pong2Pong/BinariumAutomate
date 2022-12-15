import configparser
import datetime
import json
import asyncio
import re
import time

from telethon.client import messages
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
from telethon import connection, events, functions
from telethon import functions, types
from array import *

import quotex_controller
from quotex_controller import QuotexAutomate
from stats import BetStat


config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

# Присваиваем значения внутренним переменным
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']
phone = config['Telegram']['phone']

client = TelegramClient(username, 10924741, api_hash)
client.connect()
client.start()

if not client.is_user_authorized():
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))


async def get_config_chat_position_by_name(chat_name):
    num_of_chats = 1
    while config.has_section(f"chat_{num_of_chats}"):
        if config[f"chat_{num_of_chats}"]['name'] == chat_name:
            return num_of_chats
        else:
            num_of_chats += 1


def check_chat_names_if_changed():
    for chat in client.iter_dialogs(folder=1):
        found = False
        num_of_chats = 1
        while config.has_section(f"chat_{num_of_chats}"):
            if chat.id == int(config[f"chat_{num_of_chats}"]['id']):
                found = True
                if chat.name != config[f"chat_{num_of_chats}"]['name']:
                    with open('config.ini', 'w', encoding="utf-8") as configfile:
                        config.set(f"chat_{num_of_chats}", "name", chat.name)
                        config.write(configfile)
                    print(f"Изменил имя у чата {chat.name}")
                break
            num_of_chats += 1
        if not found:
            add_chat_in_config(chat)



async def get_config_chat_position_by_id(chat_id):
    num_of_chats = 1
    while config.has_section(f"chat_{num_of_chats}"):
        if config[f"chat_{num_of_chats}"]['id'] == chat_id:
            return num_of_chats
        else:
            num_of_chats += 1


def add_chat_in_config(chat):
    num_of_chat = get_number_of_listening_chats()+1
    config.add_section(f"chat_{num_of_chat}")
    config[f"chat_{num_of_chat}"]["name"] = str(chat.name)
    config[f"chat_{num_of_chat}"]["id"] = str(chat.id)
    config[f"chat_{num_of_chat}"]["language"] = 'default'
    config[f"chat_{num_of_chat}"]["max_signal_length"] = str(30)
    config[f"chat_{num_of_chat}"]["right_signals"] = str(0)
    config[f"chat_{num_of_chat}"]["wrong_signals"] = str(0)
    with open('config.ini', 'w', encoding="utf-8") as configfile:
        config.write(configfile)
    print(f"Добавил чат {chat.name} в конфиг файл")


def get_listening_chat_names():
    num_of_chats = 1
    chat_names = []
    while config.has_section(f"chat_{num_of_chats}"):
        if config[f"chat_{num_of_chats}"]['name'] in [chat.name for chat in client.iter_dialogs()]:
            chat_names.append(config[f"chat_{num_of_chats}"]['name'])
        else:
            print("Канал ", config[f"chat_{num_of_chats}"]['name'], "переименован")
        num_of_chats += 1
    return chat_names


def get_number_of_listening_chats():
    num_of_chats = 1
    while config.has_section(f"chat_{num_of_chats}"):
        num_of_chats += 1
    return num_of_chats - 1


def get_chat_name_by_id(chat_id):
    result = []
    for chat in client.iter_dialogs():
        if chat.id == chat_id:
            result.append({chat.name: chat.id})
    return result


async def a_get_chat_name_by_id(chat_id):
    async for chat in client.iter_dialogs():
        if chat.id == chat_id:
            return chat.name


def get_listening_chat_names_from_archive():
    num_of_chats = 1
    chat_names = []
    for chat in client.iter_dialogs(folder=1):
        chat_names.append(chat.name)
    return chat_names


@client.on(events.NewMessage(get_listening_chat_names_from_archive()))
async def my_event_handler(event):
    direction = 'XXX'
    bet_time = 0
    bet_time_multiplier = 0
    chat_language = ""
    chat_config_position = await get_config_chat_position_by_name(event.chat.title)
    signal_time = event.message.date + datetime.timedelta(hours=3)
    print(event.message.to_dict()['message'])

    try:
        if config.has_section(f"chat_{chat_config_position}"):
            config_chat_section = f"chat_{chat_config_position}"
            if config.has_option(config_chat_section, "language"):
                if config[config_chat_section]["language"].lower() != "default":
                    chat_language = config[config_chat_section]["language"]
                else:
                    print("Не установлен язык чата, выбран по умолчанию")
                    chat_language = "Russian"
    except:
        print("Не установлен язык чата, выбран по умолчанию")
        chat_language = "Russian"

    bet_words_up = config[chat_language]["default_direction_up"].split()
    bet_words_down = config[chat_language]["default_direction_down"].split()
    bet_words_minute = config[chat_language]["default_minute"].split()

    for word in re.findall(r'\w+', event.message.message.lower()):
        for check_word in bet_words_up:
            if word == check_word and direction == 'XXX':
                direction = 'вверх'
        for check_word in bet_words_down:
            if word == check_word and direction == 'XXX':
                direction = 'вниз'
        if word.isdigit() and bet_time == 0:
            bet_time = int(word)
        for check_word in bet_words_minute:
            if word == check_word:
                bet_time_multiplier = 1
                if word == "минуту":
                    bet_time = 1

    if direction != 'XXX' and bet_time * bet_time_multiplier > 0 and \
            len(event.message.to_dict()['message'].lower().split()) < \
            int(config[f"chat_{chat_config_position}"]["max_signal_length"]):
        currency = await find_last_currency(event.message.peer_id.channel_id)
        print(
            f"В {signal_time} На канале {event.chat.title} я распознал это как ставку {direction} на {bet_time} мин на {currency} валютной паре ")
        bet = BetStat(direction, bet_time, signal_time, event.chat.title, currency)


async def send_log(result, chat_name, direction, bet_time, delay, open_currency, close_currency):
    dump_history = []
    await client.send_message('Log', f"{result} На канале {chat_name} {time.ctime()}")
    try:
        with open(f'Logs/BetLogs/{datetime.date.today()}.json', 'r', encoding="utf-8") as outfile:
            dump_history = json.load(outfile)
    except:
        pass
    dump_history.append(f"{result} На канале {chat_name} с задержкой {delay} {direction} на {bet_time} мин в {time.ctime()}, начальная {open_currency}, конечная {close_currency}/n")
    with open(f'Logs/BetLogs/{datetime.date.today()}.json', 'w', encoding="utf-8") as outfile:
        json.dump(dump_history, outfile, indent=4, ensure_ascii=False)


async def find_last_currency(chat_name):
    number_of_counted_words = 0
    found_currency = ''
    async for mes in client.iter_messages(chat_name):
        try:
            for word in re.findall(r'\w+', mes.message.upper()):
                for check_word in config["General"]["default_currency"].split():
                    if word == check_word:
                        number_of_counted_words += 1
                        if found_currency != '':
                            found_currency += '/'
                            found_currency += word
                        else:
                            found_currency += word
            if number_of_counted_words == 2:
                return found_currency
        except Exception:
            print("Exception on ", mes)
        number_of_counted_words = 0
        found_currency = ''


def get_all_chats_id():
    result = []
    for chat in client.iter_dialogs():
        result.append({chat.name: chat.id})
    return result


def get_chat_id(chat_name):
    for chat in client.iter_dialogs():
        if chat.name == chat_name:
            return chat.id


async def a_get_chat_history_bets(chat_name):
    number_of_read_messages = 0
    number_of_counted_words = 0
    number_of_founded_numeric = 0
    output = []
    check_words = config["General"]["default_bet_words"].split()
    print(client.iter_messages(chat_name))
    async for mes in client.iter_messages(chat_name):

        number_of_read_messages += 1
        if number_of_read_messages % 100 == 0:
            print(f"{chat_name} Прочтено {number_of_read_messages} сообщений, среди них ставок - {len(output)}")

        try:
            for word in mes.message.lower().split():
                if word.isdigit():
                    number_of_counted_words += 1
                    number_of_founded_numeric += 1
                else:
                    for check_word in check_words:
                        if check_word in word:
                            number_of_counted_words += 1
        except:
            print(f"Exception Сообщение {mes} не было разобрано")

        if number_of_counted_words == 3 and number_of_founded_numeric == 1:
            output.append(mes.message)
        number_of_counted_words = 0
        number_of_founded_numeric = 0

    with open(f'Logs\\a_chat_history_bets_log___{chat_name}.txt', 'w', encoding="utf-8") as outfile:
        json.dump(output, outfile, indent=4, ensure_ascii=False)
    print(f"----{chat_name}----Итого было всего прочтено {number_of_read_messages} сообщений")


async def a_get_messages_from_users(chat_name):
    outfile = open(f"'a_get_messages_from_users' of {chat_name}.txt", 'w', encoding="utf-8")
    read_messages = 0
    unread_messages = 0
    output = {}

    async for partic in client.iter_participants(chat_name):
        try:
            output[partic.id] = [partic.first_name + " " + partic.last_name, 0]
        except Exception:
            try:
                output[partic.id] = [partic.first_name, 0]
            except Exception:
                print(f"При получении информации об {partic} произошла ошибка")

    print(output)
    async for mes in client.iter_messages(chat_name):
        # if mes.action == "MessageActionChatAddUser":
        #
        #     print(f"Сообщение {mes} было проигнорировано")
        #     continue

        try:
            output[mes.from_id.user_id][1] += 1
            read_messages += 1
        except Exception:
            try:
                output[mes.from_id.user_id] = [mes.from_id.user_id, 0]
            except Exception:
                print(f"Exception Сообщение {mes} не было разобрано")
                unread_messages += 1
                read_messages += 1

        if read_messages % 100 == 0:
            print(
                f"{chat_name} Прочтено {read_messages} сообщений, не разобрано {unread_messages} текущие показатели: ",
                output)
    print(f"----{chat_name}----Итого было всего прочтено {read_messages} сообщений, итоговые показатели: ",
          output)
    with open(f'Logs\\chat_history_bets_log_{chat_name}.txt', 'w', encoding="utf-8") as outfile:
        json.dump(output, outfile, indent=4, ensure_ascii=False)


def dump_all_chats():
    with open('data.txt', 'w', encoding="utf-8") as outfile:
        json.dump(get_all_chats_id(), outfile, indent=4, ensure_ascii=False)
    # print("telegram_controller запущен")


# async def a_main():
#     task1 = asyncio.create_task(check_chat_names_if_changed())
#     await task1


# def main():
#     with open('data.txt', 'w', encoding="utf-8") as outfile:
#         json.dump(get_all_chats_id(), outfile, indent=4, ensure_ascii=False)
#     print("telegram_controller запущен")


# main()
# with client:
#     client.loop.run_until_complete(a_main())

check_chat_names_if_changed()
print("Telegram_controller запущен")

