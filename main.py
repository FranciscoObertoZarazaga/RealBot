from UserInterface import SOCKETIO, APP, USER_INTERFACE
from Binance import WS
from Telegram import TELEGRAM
from Bot import BOT
from Tester import TESTER
from threading import Thread
import warnings
warnings.filterwarnings("ignore")

WS.subscribe(BOT)
BOT.subscribe([TESTER, USER_INTERFACE])

threads = list()
threads.append(Thread(target=WS.run, name='bot'))
threads.append(Thread(target=TELEGRAM.start, daemon=True))
#threads.append(Thread(target=SOCKETIO.run,kwargs={"app": APP},name='iu'))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

