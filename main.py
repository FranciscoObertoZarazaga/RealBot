from Bot import Bot

from Binance import WebSocketBinance
from time import sleep
import threading
import warnings
warnings.filterwarnings("ignore")



bot = Bot()
ws = WebSocketBinance()
ws.subscribe(bot)
ws.run()


'''
while True:
    kl.load()
    kline = kl.getKlines()
    print(kline)
    points = 0
    points += WinStrategy(kline,)

    if points > 0:
        trader.buy()
        print('Compra')
        notify('Comprá')
    elif points < 0:
        trader.sell()
        print('Vende')
        notify('Vendé')
    open('state','w').write(f'ACTIVO: {datetime.now().strftime("%H:%M %d-%m-%Y")}')
    trader.wait()




'''


