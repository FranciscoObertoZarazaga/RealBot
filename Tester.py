from Config import THREADS, INTERVALS, IS_REAL_TRADER, SYMBOL, ASSET, FIAT
from Binance import BINANCE
from datetime import datetime
from time import sleep
from Bot import BOT
import pytz
from Wallet import WALLET


class Tester:
    def __init__(self):
        super(Tester, self).__init__()
        self.last_activity = None

    def test_thread(self):
        return THREADS['bot'].is_alive()

    def set_last_activity(self):
        self.last_activity = datetime.now(tz=pytz.timezone('America/Cordoba')).strftime("%H:%M %d-%m-%Y")

    def test(self):
        bot_thread = self.test_thread()
        msg = f'Thread: {"On" if bot_thread else "Off"}'
        msg += f'\nLast update: {self.last_activity}'
        msg += f'\nBot: {"On" if BOT.on else "Off"}'
        msg += f'\nStatus: {"In" if BOT.last_status else "Out"}'
        msg += f'\nSymbol: {SYMBOL}'
        msg += f'\nInterval: {INTERVALS}'
        msg += f'\nWallet: {BINANCE.get_usdt()} USDT , {BINANCE.get_crypto(ASSET)} {ASSET}' if IS_REAL_TRADER else f'\nWallet: {WALLET.getAmount(FIAT)} {FIAT} , {WALLET.getAmount(ASSET)} {ASSET}'
        diagnostic = {
            'bot_thread': bot_thread,
            'last_activity': self.last_activity,
            'msg': msg
        }
        return diagnostic

    def run(self):
        while True:
            sleep(1)
            diagnostic = self.test()
            if diagnostic.get('bot_thread'):
                BOT.restart()

    def restart(self):
        pass


TESTER = Tester()
