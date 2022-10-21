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

import quotex_controller


quotex = quotex_controller.QuotexAutomate()

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


def get_listening_chat_names():
    num_of_chats = 1
    chat_names = []
    while config.has_section(f"chat_{num_of_chats}"):
        chat_names.append(config[f"chat_{num_of_chats}"]['name'])
        num_of_chats += 1
    return chat_names


def get_number_of_listening_chats():
    num_of_chats = 1
    while config.has_section(f"chat_{num_of_chats}"):
        num_of_chats += 1
    return num_of_chats - 1


@client.on(events.NewMessage(get_listening_chat_names()))
async def my_event_handler(event):
    direction = 'XXX'
    bet_time = 0
    chat_name = ''
    currency = ''
    print(event.message.to_dict()['message'])
    if len(event.message.to_dict()['message'].split()) != 3:
        print("Сообщение не распознано")
        return 0
    for word in event.message.to_dict()['message'].lower().split():
        if word in 'вверх' and direction == 'XXX':
            direction = 'вверх'
        elif word in 'вниз' and direction == 'XXX':
            direction = 'вниз'
        elif word.isdigit():
            bet_time = int(word)
        elif 'минут' in word:
            continue
        else:
            print("Сообщение не распознано")
            return 0
    if direction != 'XXX' and bet_time > 0:
        currency = await find_last_currency(event.message.peer_id.channel_id)
        print(f"Я распознал это как ставку {direction} на {bet_time} мин на {currency} валютной паре")
        quotex.make_bet(direction, bet_time, currency)


def find_last_currency_old(chat_name):
    number_of_counted_words = 0
    output = []
    for mes in client.iter_messages(chat_name):
        try:
            # print(mes.message, re.split(r'\w+', mes.message.heigher()))
            for word in re.findall(r'\w+', mes.message.upper()):
                for check_word in config["General"]["default_currency"].split():
                    if word == check_word:
                        number_of_counted_words += 1
            if number_of_counted_words == 2:
                output.append([mes.message, mes.id])
                print("НАШЕЛ СТРОЧКУ ---> ", mes.message)
            number_of_counted_words = 0
        except Exception:
            print("Exception on ",mes)
    print(output)
    with open(f'find_last_currency_of_{chat_name}.txt', 'w', encoding="utf-8") as outfile:
        json.dump(output, outfile, indent=4, ensure_ascii=False)


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


def get_chat_history_bets(chat_name):
    number_of_counted_words = 0
    number_of_founded_numeric = 0
    output = []
    for mes in client.iter_messages(chat_name):
        try:
            for word in mes.to_dict()['message'].lower().split():
                if word.isdigit():
                    number_of_counted_words += 1
                    number_of_founded_numeric += 1
                else:
                    for check_word in config["General"]["default_bet_words"].split():
                        if word == check_word:
                            number_of_counted_words += 1
            if number_of_counted_words == 3 and number_of_founded_numeric == 1:
                output.append(mes.message, mes)
                print(mes.message)
            number_of_counted_words = 0
            number_of_founded_numeric = 0
        except Exception:
            print(mes)
    with open(f'chat_history_bets_log_{chat_name}.txt', 'w', encoding="utf-8") as outfile:
        json.dump(output, outfile, indent=4, ensure_ascii=False)


async def a_get_chat_history_bets(chat_name):
    number_of_counted_words = 0
    number_of_founded_numeric = 0
    for mes in client.iter_messages(chat_name):
        for word in mes.to_dict()['message'].lower().split():
            if word.isdigit():
                number_of_counted_words += 1
                number_of_founded_numeric += 1
            else:
                for check_word in config["General"]["default_bet_words"].split():
                    if word == check_word:
                        number_of_counted_words += 1
        if number_of_counted_words == 3 and number_of_founded_numeric == 1:
            print(mes.to_dict()['message'])
        number_of_counted_words = 0
        number_of_founded_numeric = 0


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
            print(f"{chat_name} Прочтено {read_messages} сообщений, не разобрано {unread_messages} текущие показатели: ",
                  output)
    print(f"----{chat_name}----Итого было всего прочтено {read_messages} сообщений, итоговые показатели: ",
          output)
    with open(f'chat_history_bets_log_{chat_name}.txt', 'w', encoding="utf-8") as outfile:
        json.dump(output, outfile, indent=4, ensure_ascii=False)


# async def a_main():
    # tasks = [
    #     # async_func(),
    #     # a_get_messages_from_users('Test Signals')
    # ]
    # await asyncio.gather(*tasks)


# def main():
#     # with open('data.txt', 'w', encoding="utf-8") as outfile:
#     #     json.dump(get_all_chats_id(), outfile, indent=4, ensure_ascii=False)
#     print("telegram_controller запущен")


# main()
# with client:
#     client.loop.run_until_complete(a_main())
