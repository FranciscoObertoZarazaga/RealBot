import time
from binance.client import Client
from binance import ThreadedWebsocketManager
from datetime import datetime
from Config import *

API_KEY = "xncgCNincYtvP9UiyHcYDtgaREI4Z34b6Lkoti9odPrCxgnZpQgTGygR6FH2FSzx"
SECRET_KEY = "nMm5SBvHYLuvmw0GacMruXrH408XWcEEC0CmzHuhhPr2c5UVSNSmYazOYQES6D4H"

class Binance:

    def __init__(self):
        self.client = Client(API_KEY, SECRET_KEY)

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
    def getOrderBook(self,symbol):
        try:
            return self.client.get_order_book(symbol=symbol,limit="1000")
        except:
            self.reconnect()
            return self.getOrderBook(symbol)

    def get_mean(self,symbol):
        try:
            return float(self.client.get_avg_price(symbol=symbol)['price'])
        except:
            self.reconnect()
            return self.get_price(symbol)

    def get_price(self,symbol):
        try:
            order_book = self.client.get_order_book(symbol=symbol,limit="1")
            #return buy_price, sell_price
            return float(order_book['asks'][0][0]), float(order_book['bids'][0][0])
        except:
            self.reconnect()
            return self.get_price(symbol)

    def get_historical_k_lines(self,symbol,interval,start_str,end_str=None):
        return self.client.get_historical_klines_generator(symbol, interval, start_str,end_str)

    def get_k_lines(self,symbol,interval,limit):
        try:
            return self.client.get_klines(symbol=symbol, interval=interval,limit=limit)
        except:
            self.reconnect()
            return self.get_k_lines(symbol,interval,limit)

    def buy(self,symbol):
        try:
            minNotional = self.getMinNotional(symbol)
            usdt = self.getusdt()
            if usdt >= minNotional:
                return self.client.order_market_buy(symbol='BTCUSDT',quoteOrderQty=usdt, newOrderRespType='ACK')
        except Exception as e:
            print(e)
            return self.buy(symbol)

    def sell(self,symbol):
        try:
            crypto = self.getbtc()
            if crypto > 0:
                return self.client.order_market_sell(symbol=symbol, quantity=crypto, newOrderRespType='ACK')
        except Exception as e:
            print(e)
            return self.sell(symbol)

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
            time.sleep(10)
            self.reconnect(0)

    def alert(self,msg):
        print('Recibido',msg)

    def getTime(self):
        return datetime.fromtimestamp(self.client.get_server_time()['serverTime'] / 1000).strftime('%H:%M %d-%m-%Y')

    def getFilters(self,symbol):
        return self.client.get_symbol_info(symbol=symbol)['filters']

    def getMinNotional(self,symbol):
        minNotional = None
        filters = self.getFilters(symbol)
        for filter in filters:
            if filter['filterType'] == 'MIN_NOTIONAL':
                minNotional = filter['minNotional']
        return minNotional


class WebSocketBinance:
    def __init__(self):
        self.ws = ThreadedWebsocketManager(api_key=API_KEY, api_secret=SECRET_KEY)
        self.ws.start()
        self.observers = list()
        self.kline_socket = None

    def subscribe(self,observer):
        self.observers.append(observer)

    def notify(self,data):
        for observer in self.observers: observer.update(data)

    def run(self):
        self.kline_socket = self.ws.start_kline_socket(callback=self.notify, symbol=SYMBOL,interval=INTERVAL)
        self.ws.join()

    def stop(self):
        assert self.kline_socket != None
        self.ws.stop_socket(self.kline_socket)

