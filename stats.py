import asyncio
import datetime
import time
import configparser

import telegram_controller
from quotex_controller import QuotexAutomate
quotex = QuotexAutomate()
class BetStat:
    bets = []
    loop = asyncio.get_event_loop()

    def __init__(self, direction, bet_time, signal_time, chat_name, currency_pair):
        self.direction = direction
        self.signal_time = signal_time
        self.start_time = datetime.datetime.fromtimestamp(time.time(), datetime.timezone.utc)
        self.bet_time = bet_time
        self.end_time = time.ctime(time.time()+int(bet_time)*60)
        self.currency_on_start = "currency_on_start"
        self.currency_on_end = "currency_on_end"
        self.result = "result"
        self.chat_name = chat_name
        BetStat.bets.append(self)
        quotex.make_bet(direction, bet_time, currency_pair)
        self.delay = self.start_time - self.signal_time + datetime.timedelta(hours=3)
        self.loop.create_task(self.wait_for_result(bet_time))

    def print_to_console(self):
        print("--Stat:",self.chat_name ,self.result, self.delay, self.direction, self.start_time.time(), self.bet_time, self.currency_on_start, self.currency_on_end)

    async def wait_for_result(self, bet_time):
        await asyncio.sleep(int(bet_time*60))
        self.currency_on_start, self.currency_on_end = QuotexAutomate.get_currency_open_close(QuotexAutomate.QA[0])
        await self.analyze_result()
        await telegram_controller.send_log(self.result, self.chat_name, self.chat_name, self.bet_time, self.delay, self.currency_on_start, self.currency_on_end)

    async def analyze_result(self):
        config = configparser.ConfigParser()
        config.read("config.ini", encoding="utf-8")
        chat_config_position = await telegram_controller.get_config_chat_position_by_name(self.chat_name)
        if self.currency_on_start != self.currency_on_end:
            if self.direction == "вниз":
                if self.currency_on_start > self.currency_on_end:
                    self.result = "Выигрыш"
                    right_signals = int(config[f"chat_{chat_config_position}"]["right_signals"])
                    right_signals += 1
                    config[f"chat_{chat_config_position}"]["right_signals"] = str(right_signals)
                    config.set(f"chat_{chat_config_position}", "right_signals", str(right_signals))
                else:
                    self.result = "Проигрыш"
                    wrong_signals = int(config[f"chat_{chat_config_position}"]["wrong_signals"])
                    wrong_signals += 1
                    config[f"chat_{chat_config_position}"]["wrong_signals"] = str(wrong_signals)
                    config.set(f"chat_{chat_config_position}", "wrong_signals", str(wrong_signals))
            if self.direction == "вверх":
                if self.currency_on_start < self.currency_on_end:
                    self.result = "Выигрыш"
                    right_signals = int(config[f"chat_{chat_config_position}"]["right_signals"])
                    right_signals += 1
                    config[f"chat_{chat_config_position}"]["right_signals"] = str(right_signals)
                    config.set(f"chat_{chat_config_position}", "right_signals", str(right_signals))
                else:
                    self.result = "Проигрыш"
                    wrong_signals = int(config[f"chat_{chat_config_position}"]["wrong_signals"])
                    wrong_signals += 1
                    config[f"chat_{chat_config_position}"]["wrong_signals"] = str(wrong_signals)
                    config.set(f"chat_{chat_config_position}", "wrong_signals", str(wrong_signals))
        with open('config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)
        self.print_to_console()
