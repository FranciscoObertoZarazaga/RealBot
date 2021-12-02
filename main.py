from Binance import WS
from Telegram import TELEGRAM
from Bot import BOT
import threading
import warnings
warnings.filterwarnings("ignore")

WS.subscribe(BOT)

threads = list()
threads.append(threading.Thread(target=WS.run, name='bot'))
threads.append(threading.Thread(target=TELEGRAM.start, daemon=True))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

