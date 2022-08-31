from Config import THREADS
from Telegram import TELEGRAM
from TradingTriangular import BOT
from Tester import TESTER
from threading import Thread
import warnings
warnings.filterwarnings("ignore")

THREADS.update({'bot': Thread(target=BOT.run, name='bot')})
THREADS.update({'telegram': Thread(target=TELEGRAM.run, name='telegram')})
#THREADS.update({'tester': Thread(target=TESTER.run, name='tester')})

for thread in THREADS.values():
    thread.start()

for thread in THREADS.values():
    thread.join()
