from time import sleep
from binance.client import Client
from binance.enums import *
from binance.exceptions import *
from datetime import datetime
from Config import INTERVAL, CONFIG
import Telegram

API_KEY = "xncgCNincYtvP9UiyHcYDtgaREI4Z34b6Lkoti9odPrCxgnZpQgTGygR6FH2FSzx"
SECRET_KEY = "nMm5SBvHYLuvmw0GacMruXrH408XWcEEC0CmzHuhhPr2c5UVSNSmYazOYQES6D4H"

def catcher(function):
    def wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except ConnectionError:
            self.reconnect()
            return function
        except BinanceAPIException as e:
            Telegram.TELEGRAM.notify(e)
            sleep(1)
        except Exception as e:
            Telegram.TELEGRAM.notify(e)

    return wrapper


class Binance:

    @catcher
    def __init__(self, api_key=API_KEY, secret_key=SECRET_KEY):
        self.client = Client(api_key, secret_key)

    @catcher
    def get_client(self):
        return self.client

    def get_status(self):
        return self.client.get_system_status()

    # Devuelve el libro de órdenes de compra y venta.
    # El Bid price es el precio máximo al que un consumidor está dispuesto a comprar
    # El Ask price es el precio mínimo al que un oferente está dispuesto a vender
    @catcher
    def get_order_book(self):
        return self.client.get_order_book(symbol=CONFIG.get_symbol(), limit="1000")

    @catcher
    def get_all_tickers(self):
        ticker = self.client.get_all_tickers()
        symbols = list()
        for symbol in ticker:
            symbols.append(symbol['symbol'])
        return symbols

    @catcher
    def getAllCoinsWith(self, fiat):
        ticker = self.client.get_all_tickers()
        coins = list()
        for symbol in ticker:
            coin = symbol['symbol']
            if fiat == coin[-(len(fiat)):]:
                coins.append(symbol['symbol'].replace(fiat, ''))
        return coins

    @catcher
    def getAllCoinsWithUSDT(self):
        return self.getAllCoinsWith('USDT')

    @catcher
    def getAllCoinsWithBTC(self):
        return self.getAllCoinsWith('BTC')

    @catcher
    def get_symbol_info(self, symbol):
        return self.client.get_symbol_info(symbol)

    @catcher
    def get_book_price(self, symbol):
        order_book = self.client.get_order_book(symbol=symbol, limit="1")
        #return buy_price, sell_price
        return float(order_book['asks'][0][0]), float(order_book['bids'][0][0])

    @catcher
    def get_all_coins(self):
        c = self.client.get_all_coins_info()
        coins = list()
        for coin in c:
            coins.append(coin['coin'])
        return coins

    @catcher
    def get_mean(self):
        return float(self.client.get_avg_price(symbol=CONFIG.get_symbol())['price'])

    @catcher
    def get_k_lines(self, limit, symbol=CONFIG.get_symbol()):
        return self.client.get_klines(symbol=symbol, interval=INTERVAL, limit=limit)

    @catcher
    def buy(self, fiat, coin):
        self.delete_all_orders()
        c1 = self.get_crypto_qty(fiat)
        if c1 is False:
            return False
        info = self.client.order_market_buy(
            symbol=coin+fiat,
            quoteOrderQty=fiat,
            newOrderRespType='ACK'
        )
        print(info)
        return True

    @catcher
    def sell(self, fiat, coin):
        self.delete_all_orders()
        crypto = self.get_crypto_qty(coin)
        if crypto is False:
            return False
        info = self.client.order_market_sell(
            symbol=coin+fiat,
            quantity=crypto,
            newOrderRespType='ACK'
        )
        print(info)
        return True

    @catcher
    def make_order(self, price, side, rate, qty=None):
        stop_price = self.get_price(price * rate)
        limit_price = self.get_price(stop_price * rate)
        if not (stop_price * limit_price * qty):
            return False
        self.client.create_order(
            symbol=CONFIG.get_symbol(),
            side=side,
            type=ORDER_TYPE_STOP_LOSS_LIMIT,
            quantity=qty,
            timeInForce=TIME_IN_FORCE_GTC,
            price=limit_price,
            stopPrice=stop_price
        )

    @catcher
    def stop_loss(self, price, stop_rate=.995):
        self.delete_all_orders()
        qty = self.get_crypto_qty()
        self.make_order(price, SIDE_SELL, stop_rate, qty)

    @catcher
    def buy_order(self, price, buy_rate=1.01):
        self.delete_all_orders()
        qty = self.get_crypto_qty(self.get_usdt_qty() / (price * buy_rate ** 2))
        self.make_order(price, SIDE_BUY, buy_rate, qty)


    def order_buy_limit(self, price, buy_rate=.95):
        qty = self.get_crypto_qty(self.get_usdt_qty() / (price * buy_rate ** 2))
        self.client.order_limit_buy(
            symbol=CONFIG.get_symbol(),
            quantity=qty,
            price=price
        )

    @catcher
    def delete_all_orders(self):
        for order in self.get_all_open_orders():
            order_id = order['orderId']
            self.client.cancel_order(
                symbol=CONFIG.get_symbol(),
                orderId=order_id
            )

    @catcher
    def get_all_open_orders(self):
        return self.client.get_open_orders(symbol=CONFIG.get_symbol())

    @catcher
    def get_last_stop_price(self):
        orders = self.get_all_open_orders()
        if len(orders) == 0:
            return None
        return float(orders[-1]['stopPrice'])

    @catcher
    def get_usdt(self):
        return self.get_crypto('USDT')

    @catcher
    def get_crypto(self, asset):
        return float(self.client.get_asset_balance(asset=asset)['free'])

    def reconnect(self, n=True):
        try:
            if n is True:
                print("Reconectando")
            self.get_status()
        except ConnectionError:
            sleep(10)
            self.reconnect(False)

    @catcher
    def get_time(self):
        return datetime.fromtimestamp(self.client.get_server_time()['serverTime'] / 1000).strftime('%H:%M %d-%m-%Y')

    @catcher
    def get_filters(self):
        return self.client.get_symbol_info(symbol=CONFIG.get_symbol())['filters']

    @catcher
    def get_min_notional(self):
        filters = self.get_filters()
        for binance_filter in filters:
            if binance_filter['filterType'] == 'MIN_NOTIONAL':
                return float(binance_filter['minNotional'])

    @catcher
    def get_qty_filters(self):
        filters = self.get_filters()
        for binance_filter in filters:
            if binance_filter['filterType'] == 'LOT_SIZE':
                return float(binance_filter['minQty']), float(binance_filter['maxQty']), float(
                    binance_filter['stepSize'])

    @catcher
    def get_price_filters(self):
        filters = self.get_filters()
        for binance_filter in filters:
            if binance_filter['filterType'] == 'PRICE_FILTER':
                return float(binance_filter['minPrice']), float(binance_filter['maxPrice']), float(
                    binance_filter['tickSize'])

    @catcher
    def get_trade(self, trade_id=None, limit=None):
        return self.client.get_my_trades(symbol=CONFIG.get_symbol(), fromId=trade_id, limit=limit)

    @catcher
    def get_last_trade(self):
        trade = self.get_trade(limit=1)
        if len(trade) == 0:
            return None
        return trade[0]

    @catcher
    def get_crypto_qty(self, crypto=None):
        min_qty, max_qty, step_size = self.get_qty_filters()
        crypto = self.get_crypto(CONFIG.get_asset()) if crypto is None else crypto
        crypto = self.set_precision(crypto, step_size)
        if crypto < min_qty:
            return False
        if crypto > max_qty:
            return False
        return crypto

    @catcher
    def get_usdt_qty(self):
        min_notional = self.get_min_notional()
        usdt = self.get_usdt()
        if usdt < min_notional:
            return False
        return usdt

    @catcher
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

    @catcher
    def set_precision(self, n, p):
        precision = round(1 / p)
        return int((n - p) * precision) / precision


    @catcher
    def is_enable(self, symbol):
        return self.client.get_symbol_info(symbol)['status'] == 'TRADING'

    @catcher
    def are_enable(self, symbols, i=0):
        if len(symbols) == i+1:
            return self.is_enable(symbols[i])
        return self.is_enable(symbols[i]) and self.are_enable(symbols, i+1)


BINANCE = Binance()
