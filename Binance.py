from time import sleep
from binance.client import Client
from binance import ThreadedWebsocketManager
from binance.enums import *
from datetime import datetime
from Observed import Observed
from Config import SYMBOL, INTERVAL
from threading import Thread
from Config import THREADS

API_KEY = "xncgCNincYtvP9UiyHcYDtgaREI4Z34b6Lkoti9odPrCxgnZpQgTGygR6FH2FSzx"
SECRET_KEY = "nMm5SBvHYLuvmw0GacMruXrH408XWcEEC0CmzHuhhPr2c5UVSNSmYazOYQES6D4H"

class Binance:

    def __init__(self, api_key=API_KEY, secret_key=SECRET_KEY):
        self.client = Client(api_key, secret_key)

    def getAllTickers(self):
        return self.client.get_all_tickers()

    #Retorna un listado de cryptomonedas disponibles en Binance
    def getAllCoins(self):
        return self.client.get_all_coins_info()

    def getClient(self):
        return self.client

    def getStatus(self):
        return self.client.get_system_status()

    #Devuelve el libro de órdenes de compra y venta.
    #El Bid price es el precio máximo al que un consumidor está dispuesto a comprar
    # El Ask price es el precio mínimo al que un oferente está dispuesto a vender
    def getOrderBook(self):
        try:
            return self.client.get_order_book(symbol=SYMBOL,limit="1000")
        except:
            self.reconnect()
            return self.getOrderBook()

    def get_mean(self):
        try:
            return float(self.client.get_avg_price(symbol=SYMBOL)['price'])
        except:
            self.reconnect()
            return self.get_price()

    def get_price(self):
        try:
            order_book = self.client.get_order_book(symbol=SYMBOL,limit="1")
            #return buy_price, sell_price
            return float(order_book['asks'][0][0]), float(order_book['bids'][0][0])
        except:
            self.reconnect()
            return self.get_price()

    def get_historical_k_lines(self,start_str,end_str=None):
        return self.client.get_historical_klines_generator(SYMBOL, INTERVAL, start_str,end_str)

    def get_k_lines(self, limit):
        try:
            return self.client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=limit)
        except:
            self.reconnect()
            return self.get_k_lines(limit)

    def buy(self):
        try:
            minNotional = self.getMinNotional()
            usdt = self.getusdt()
            if usdt >= minNotional:
                self.client.order_market_buy(
                    symbol=SYMBOL,
                    quoteOrderQty=usdt,
                    newOrderRespType='ACK'
                )
                return True
            return False
        except Exception as e:
            print(e)

    def sell(self):
        try:
            minQty, maxQty, stepSize, minPrice, maxPrice, tickSize = self.get_sell_filters()
            crypto = self.getbtc()
            crypto = crypto - crypto % stepSize
            if crypto >= minQty and crypto <= maxQty:
                self.client.order_market_sell(
                    symbol=SYMBOL,
                    quantity=crypto,
                    newOrderRespType='ACK'
                )
                return True
            return False
        except Exception as e:
            print(e)

    def stop_loss(self):
        _, last_price = self.get_price()
        last_stop_price = self.get_last_stop_price()
        if last_stop_price is not None:
            if last_price <= last_stop_price:
                return 0
            self.delete_all_orders()
        minQty, maxQty, stepSize, minPrice, maxPrice, tickSize = self.get_sell_filters()
        stop_price = last_price * .98
        limit_price = stop_price * .95
        precision = len(str(tickSize)) - len(str(round(tickSize))) - 1
        stop_price = round(stop_price, precision)
        limit_price = round(limit_price, precision)
        if stop_price >= maxPrice and stop_price <= minPrice and limit_price >= maxPrice and limit_price <= minPrice:
            return 0
        crypto = self.getbtc()
        crypto = crypto - crypto % stepSize
        try:
            if crypto >= minQty and crypto <= maxQty:
                self.client.create_order(
                    symbol=SYMBOL,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_STOP_LOSS_LIMIT,
                    quantity=crypto,
                    timeInForce=TIME_IN_FORCE_GTC,
                    price=limit_price,
                    stopPrice=stop_price
                )
        except Exception as e:
            print(e)

    def delete_all_orders(self):
        for order in self.get_all_open_orders():
            order_id = order['orderId']
            self.client.cancel_order(
                symbol=SYMBOL,
                orderId=order_id
            )

    def get_all_open_orders(self):
        return self.client.get_open_orders(symbol=SYMBOL)

    def get_last_stop_price(self):
        orders = self.get_all_open_orders()
        if len(orders) == 0:
            return None
        return float(orders[-1]['stopPrice'])

    def getusdt(self):
        return self.getCrypto('USDT')

    def getbtc(self):
        return self.getCrypto('BTC')

    def getCrypto(self,asset):
        return float(self.client.get_asset_balance(asset=asset)['free'])

    def reconnect(self,n=1):
        try:
            if n==1:
                print("Reconectando")
            self.getStatus()
        except:
            sleep(10)
            self.reconnect(0)

    def alert(self,msg):
        print('Recibido',msg)

    def getTime(self):
        return datetime.fromtimestamp(self.client.get_server_time()['serverTime'] / 1000).strftime('%H:%M %d-%m-%Y')

    def getFilters(self):
        return self.client.get_symbol_info(symbol=SYMBOL)['filters']

    def getMinNotional(self):
        minNotional = None
        filters = self.getFilters()
        for filter in filters:
            if filter['filterType'] == 'MIN_NOTIONAL':
                minNotional = filter['minNotional']
        return float(minNotional)

    def get_sell_filters(self):
        filters = self.getFilters()
        minQty, maxQty, stepSize, minPrice, maxPrice, tickSize = range(6)
        for filter in filters:
            if filter['filterType'] == 'LOT_SIZE':
                minQty, maxQty, stepSize = float(filter['minQty']), float(filter['maxQty']), float(filter['stepSize'])
            if filter['filterType'] == 'PRICE_FILTER':
                minPrice, maxPrice, tickSize = float(filter['minPrice']), float(filter['maxPrice']), float(filter['tickSize'])
        return minQty, maxQty, stepSize, minPrice, maxPrice, tickSize

    def get_trade(self, trade_id=None, limit=None):
        return self.client.get_my_trades(symbol=SYMBOL, fromId=trade_id, limit=limit)

    def get_last_trade(self):
        return self.get_trade(limit=1)[0]

    def get_trade_with_id(self, trade_id):
        return self.get_trade(SYMBOL, trade_id=trade_id, limit=1)[0]

class WebSocketBinance(Observed):
    def __init__(self):
        super(WebSocketBinance, self).__init__()
        self.ws = ThreadedWebsocketManager(api_key=API_KEY, api_secret=SECRET_KEY)
        self.kline_socket = None

    def run(self):
        if not self.ws.is_alive():
            self.ws.start()
            self.kline_socket = self.ws.start_kline_socket(callback=self.notify, symbol=SYMBOL,interval=INTERVAL)
            self.ws.join()

    def start(self):
        THREADS.update({'bot': Thread(target=self.run, name='bot')})
        THREADS['bot'].start()

    def stop(self):
        if self.ws.is_alive():
            assert self.kline_socket is not None
            self.ws.stop_socket(self.kline_socket)
            self.ws.stop()
            self.ws = ThreadedWebsocketManager(api_key=API_KEY, api_secret=SECRET_KEY)

    def restart(self, t=0):
        self.stop()
        sleep(t)
        self.start()


    def notify(self,data):
        try:
            super().notify(data)
        except Exception as e:
            print(e)
            self.restart()


BINANCE = Binance()
WS = WebSocketBinance()


