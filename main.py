from Config import THREADS, IS_BACKTEST
from Telegram import TELEGRAM
from Bot import BOT
from Tester import TESTER
from threading import Thread
import warnings
warnings.filterwarnings("ignore")


print('Running...')

if IS_BACKTEST:
    THREADS.update({'bot': Thread(target=BOT.backtest, name='bot')})
else:
    THREADS.update({'bot': Thread(target=BOT.run, name='bot')})

THREADS.update({'telegram': Thread(target=TELEGRAM.run, name='telegram')})
#THREADS.update({'tester': Thread(target=TESTER.run, name='tester', daemon=True)})

for thread in THREADS.values():
    thread.start()

for thread in THREADS.values():
    thread.join()
