import asyncio
import time

from quotex_controller import QuotexAutomate


class BetStat:
    bets = []
    loop = asyncio.get_event_loop()

    def __init__(self, direction, bet_time, signal_time):
        self.direction = direction
        self.signal_time = signal_time
        self.start_time = time.ctime()
        self.bet_time = bet_time
        self.end_time = time.ctime(time.time()+int(bet_time)*60)
        self.currency_on_start = "currency_on_start"
        self.currency_on_end = "currency_on_end"
        self.result = "result"
        BetStat.bets.append(self)
        self.loop.create_task(self.wait_for_result(bet_time))
        print("Created BetStat")

    def print_to_console(self):
        print(self.direction, self.start_time, self.bet_time, self.end_time, self.currency_on_start, self.currency_on_end)

    @staticmethod
    def printHello():
        print("Hello")

    async def wait_for_result(self, bet_time):
        await asyncio.sleep(int(bet_time))
        self.currency_on_start, self.currency_on_end = QuotexAutomate.get_currency_open_close()
        QuotexAutomate.get_currency_open_close()
        self.print_to_console()


BetStat.printHello()
