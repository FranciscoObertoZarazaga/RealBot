from Bot import Bot
from Telegram import BotTelegram
from Tester import Tester
from Binance import WebSocketBinance
from time import sleep
import threading
import warnings
warnings.filterwarnings("ignore")

tester = Tester()
telegram = BotTelegram(tester)

bot = Bot(telegram, tester)
ws = WebSocketBinance()
ws.subscribe(bot)

threads = list()
threads.append(threading.Thread(target=ws.run, name='bot'))
threads.append(threading.Thread(target=telegram.start))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

