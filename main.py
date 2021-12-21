from Config import THREADS
from Binance import WS
from UserInterface import SOCKETIO, APP
from Telegram import TELEGRAM
from Bot import BOT
from Tester import TESTER
from threading import Thread
import warnings
warnings.filterwarnings("ignore")

WS.subscribe(BOT)
TESTER.subscribe(SOCKETIO)

THREADS.update({'bot':Thread(target=WS.run, name='bot')})
#THREADS.update({'telegram':Thread(target=TELEGRAM.run, name='telegram')})
#THREADS.update({'iu':Thread(target=SOCKETIO.run, kwargs={"app": APP}, name='iu')})
THREADS.update({'tester': Thread(target=TESTER.run, name='tester')})

for thread in THREADS.values():
    thread.start()

for thread in THREADS.values():
    thread.join()

