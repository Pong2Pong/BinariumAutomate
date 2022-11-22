import asyncio
import time

# from quotex_controller import QuotexAutomate


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

    def print_to_console(self):
        print("    Stat:",self.result ,self.direction, self.start_time, self.bet_time, self.end_time, self.currency_on_start, self.currency_on_end)

    async def wait_for_result(self, bet_time):
        from quotex_controller import QuotexAutomate
        await asyncio.sleep(int(bet_time*60))
        self.currency_on_start, self.currency_on_end = QuotexAutomate.get_currency_open_close(QuotexAutomate.QA[0])
        self.analyze_result()
        self.print_to_console()

    def analyze_result(self):
        if self.direction == "вниз":
            if self.currency_on_start > self.currency_on_end:
                self.result = "Выйгрыш"
            else:
                self.result = "Проигрыш"
        if self.direction == "вверх":
            if self.currency_on_start < self.currency_on_end:
                self.result = "Выйгрыш"
            else:
                self.result = "Проигрыш"
