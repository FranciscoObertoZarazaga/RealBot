from time import sleep
from binance.client import Client
from binance.enums import *
from datetime import datetime
from Config import INTERVAL, CONFIG
import Telegram


API_KEY = "xncgCNincYtvP9UiyHcYDtgaREI4Z34b6Lkoti9odPrCxgnZpQgTGygR6FH2FSzx"
SECRET_KEY = "nMm5SBvHYLuvmw0GacMruXrH408XWcEEC0CmzHuhhPr2c5UVSNSmYazOYQES6D4H"


class Binance:

    def __init__(self, api_key=API_KEY, secret_key=SECRET_KEY):
        self.client = Client(api_key, secret_key)

    def get_client(self):
        return self.client

    def get_status(self):
        return self.client.get_system_status()

    #Devuelve el libro de órdenes de compra y venta.
    #El Bid price es el precio máximo al que un consumidor está dispuesto a comprar
    # El Ask price es el precio mínimo al que un oferente está dispuesto a vender
    def get_order_book(self):
        try:
            return self.client.get_order_book(symbol=CONFIG.get_symbol(), limit="1000")
        except:
            self.reconnect()
            return self.get_order_book()

    def get_all_tickers(self):
        ticker = self.client.get_all_tickers()
        symbols = list()
        for symbol in ticker:
            symbols.append(symbol['symbol'])
        return symbols

    def get_all_coins(self):
        c = self.client.get_all_coins_info()
        coins = list()
        for coin in c:
            coins.append(coin['coin'])
        return coins

    def get_mean(self):
        try:
            return float(self.client.get_avg_price(symbol=CONFIG.get_symbol())['price'])
        except:
            self.reconnect()
            return self.get_book_price()

    def get_book_price(self):
        try:
            order_book = self.client.get_order_book(symbol=CONFIG.get_symbol(),limit="1")
            #return buy_price, sell_price
            return float(order_book['asks'][0][0]), float(order_book['bids'][0][0])
        except:
            self.reconnect()
            return self.get_book_price()

    def get_k_lines(self, limit, symbol=CONFIG.get_symbol()):
        try:
            return self.client.get_klines(symbol=symbol, interval=INTERVAL, limit=limit)
        except:
            self.reconnect()
            return self.get_k_lines(limit)

    def buy(self):
        try:
            self.delete_all_orders()
            usdt = self.get_usdt_qty()
            if usdt is False:
                return False
            self.client.order_market_buy(
                symbol=CONFIG.get_symbol(),
                quoteOrderQty=usdt,
                newOrderRespType='ACK'
            )
            return True
        except Exception as e:
            Telegram.TELEGRAM.notify('Compra: ' + str(e))

    def sell(self):
        try:
            self.delete_all_orders()
            crypto = self.get_crypto_qty()
            if crypto is False:
                return False
            self.client.order_market_sell(
                symbol=CONFIG.get_symbol(),
                quantity=crypto,
                newOrderRespType='ACK'
            )
            return True
        except Exception as e:
            Telegram.TELEGRAM.notify('Venta: ' + str(e))

    def make_order(self, price, side, rate, qty=None):
        stop_price = self.get_price(price * rate)
        limit_price = self.get_price(stop_price * rate)
        if not (stop_price * limit_price * qty):
            return False
        try:
            self.client.create_order(
                symbol=CONFIG.get_symbol(),
                side=side,
                type=ORDER_TYPE_STOP_LOSS_LIMIT,
                quantity=qty,
                timeInForce=TIME_IN_FORCE_GTC,
                price=limit_price,
                stopPrice=stop_price
            )
        except Exception as e:
            Telegram.TELEGRAM.notify('Orden: ' + str(e))

    def stop_loss(self, price, stop_rate=.995):
        self.delete_all_orders()
        qty = self.get_crypto_qty()
        self.make_order(price, SIDE_SELL, stop_rate, qty)

    def buy_order(self, price, buy_rate=1.01):
        self.delete_all_orders()
        qty = self.get_crypto_qty(self.get_usdt_qty() / (price * buy_rate**2))
        self.make_order(price, SIDE_BUY, buy_rate, qty)

    def delete_all_orders(self):
        for order in self.get_all_open_orders():
            order_id = order['orderId']
            self.client.cancel_order(
                symbol=CONFIG.get_symbol(),
                orderId=order_id
            )

    def get_all_open_orders(self):
        return self.client.get_open_orders(symbol=CONFIG.get_symbol())

    def get_last_stop_price(self):
        orders = self.get_all_open_orders()
        if len(orders) == 0:
            return None
        return float(orders[-1]['stopPrice'])

    def get_usdt(self):
        return self.get_crypto('USDT')

    def get_crypto(self, asset):
        return float(self.client.get_asset_balance(asset=asset)['free'])

    def reconnect(self,n=1):
        try:
            if n == 1:
                print("Reconectando")
            self.get_status()
        except:
            sleep(10)
            self.reconnect(0)

    def get_time(self):
        return datetime.fromtimestamp(self.client.get_server_time()['serverTime'] / 1000).strftime('%H:%M %d-%m-%Y')

    def get_filters(self):
        return self.client.get_symbol_info(symbol=CONFIG.get_symbol())['filters']

    def get_min_notional(self):
        filters = self.get_filters()
        for binance_filter in filters:
            if binance_filter['filterType'] == 'MIN_NOTIONAL':
                return float(binance_filter['minNotional'])

    def get_qty_filters(self):
        filters = self.get_filters()
        for binance_filter in filters:
            if binance_filter['filterType'] == 'LOT_SIZE':
                return float(binance_filter['minQty']), float(binance_filter['maxQty']), float(binance_filter['stepSize'])

    def get_price_filters(self):
        filters = self.get_filters()
        for binance_filter in filters:
            if binance_filter['filterType'] == 'PRICE_FILTER':
                return float(binance_filter['minPrice']), float(binance_filter['maxPrice']), float(binance_filter['tickSize'])

    def get_trade(self, trade_id=None, limit=None):
        return self.client.get_my_trades(symbol=CONFIG.get_symbol(), fromId=trade_id, limit=limit)

    def get_last_trade(self):
        trade = self.get_trade(limit=1)
        if len(trade) == 0:
            return None
        return trade[0]

    def get_crypto_qty(self, crypto=None):
        min_qty, max_qty, step_size = self.get_qty_filters()
        crypto = self.get_crypto(CONFIG.get_asset()) if crypto is None else crypto
        crypto = self.set_precision(crypto, step_size)
        if crypto < min_qty:
            return False
        if crypto > max_qty:
            return False
        return crypto

    def get_usdt_qty(self):
        min_notional = self.get_min_notional()
        usdt = self.get_usdt()
        if usdt < min_notional:
            return False
        return usdt

    def get_price(self, price):
        try:
            min_price, max_price, tick_size = self.get_price_filters()
            price = self.set_precision(price, tick_size)
            if price < min_price:
                return False
            if price > max_price:
                return False
            return price
        except ConnectionError:
            self.reconnect()

    def set_precision(self, n, p):
        precision = round(1 / p)
        return int((n-p) * precision) / precision

BINANCE = Binance()


