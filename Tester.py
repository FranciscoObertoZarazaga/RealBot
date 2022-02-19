from Config import THREADS, INTERVAL, CONFIG
from Binance import BINANCE
from datetime import datetime
from time import sleep
from Bot import BOT
import pytz


class Tester:
    def __init__(self):
        super(Tester, self).__init__()
        self.last_activity = None
        self.is_runnable = True

    def test_thread(self):
        return THREADS['bot'].is_alive()

    def set_last_activity(self):
        self.last_activity = datetime.now(tz=pytz.timezone('America/Cordoba')).strftime("%H:%M %d-%m-%Y")

    def test(self):
        test_ws = self.test_thread()
        msg = f'Thread: {"On" if test_ws else "Off"}'
        msg += f'\nLast update: {self.last_activity}'
        msg += f'\nBot: {"On" if BOT.on else "Off"}'
        msg += f'\nStatus: {"Long" if BOT.last_status else "Short"}'
        msg += f'\nSymbol: {CONFIG.get_symbol()}'
        msg += f'\nInterval: {INTERVAL}'
        msg += f'\nWallet: {BINANCE.get_usdt()} USDT , {BINANCE.get_crypto(CONFIG.get_asset())} {CONFIG.get_asset()}'
        diagnostic = {
            'test_ws': test_ws,
            'last_activity': self.last_activity,
            'msg': msg
        }
        return diagnostic

    def run(self):
        while self.is_runnable:
            sleep(3)
            diagnostic = self.test()

    def restart(self):
        pass


TESTER = Tester()
