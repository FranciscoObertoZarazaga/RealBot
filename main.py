from Bot import Bot
from binance.enums import *
from Binance import WebSocketBinance
from time import sleep
import threading
import warnings
warnings.filterwarnings("ignore")

is_real_trader = False

asset = 'BTC'
fiat = 'USDT'
symbol = asset + fiat
interval = KLINE_INTERVAL_4HOUR

bot = Bot(asset, symbol, interval, is_real_trader)
ws = WebSocketBinance()
ws.subscribe(bot)
ws.add(symbol=symbol,interval=interval)


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


