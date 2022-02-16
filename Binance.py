from time import sleep
from binance.client import Client
from binance.enums import *
from datetime import datetime
from Config import SYMBOL, INTERVAL


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
            return self.client.get_order_book(symbol=SYMBOL, limit="1000")
        except:
            self.reconnect()
            return self.get_order_book()

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

    def get_k_lines(self, limit):
        try:
            return self.client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=limit)
        except:
            self.reconnect()
            return self.get_k_lines(limit)

    def buy(self):
        try:
            min_notional = self.get_min_notional()
            usdt = self.get_usdt()
            if usdt < min_notional:
                return False
            self.client.order_market_buy(
                symbol=SYMBOL,
                quoteOrderQty=usdt,
                newOrderRespType='ACK'
            )
            return True
        except Exception as e:
            print(e)

    def sell(self):
        try:
            min_qty, max_qty, step_size, min_price, max_price, tick_size = self.get_sell_filters()
            crypto = self.get_btc()
            crypto = crypto - crypto % step_size
            if crypto < min_qty:
                return False
            if crypto > max_qty:
                return False
            self.client.order_market_sell(
                symbol=SYMBOL,
                quantity=crypto,
                newOrderRespType='ACK'
            )
            return True
        except Exception as e:
            print(e)

    def stop_loss(self):
        _, last_price = self.get_price()
        last_stop_price = self.get_last_stop_price()
        if last_stop_price is not None:
            if last_price <= last_stop_price:
                return 0
            self.delete_all_orders()
        min_qty, max_qty, step_size, min_price, max_price, tick_size = self.get_sell_filters()
        stop_price = last_price * .98
        limit_price = stop_price * .95
        precision = len(str(tick_size)) - len(str(round(tick_size))) - 1
        stop_price = round(stop_price, precision)
        limit_price = round(limit_price, precision)
        if stop_price >= max_price or stop_price <= min_price or limit_price >= max_price or limit_price <= min_price:
            return 0
        crypto = self.get_btc()
        crypto = crypto - crypto % step_size
        if crypto <= min_qty or crypto >= max_qty:
            return 0
        try:
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

    def get_usdt(self):
        return self.get_crypto('USDT')

    def get_btc(self):
        return self.get_crypto('BTC')

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
        return self.client.get_symbol_info(symbol=SYMBOL)['filters']

    def get_min_notional(self):
        min_notional = None
        filters = self.get_filters()
        for binance_filter in filters:
            if binance_filter['filterType'] == 'MIN_NOTIONAL':
                min_notional = binance_filter['minNotional']
        return float(min_notional)

    def get_sell_filters(self):
        filters = self.get_filters()
        min_qty, max_qty, step_size, min_price, max_price, tick_size = range(6)
        for binance_filter in filters:
            if binance_filter['filterType'] == 'LOT_SIZE':
                min_qty, max_qty, step_size = float(binance_filter['minQty']), float(binance_filter['maxQty']), float(binance_filter['stepSize'])
            if binance_filter['filterType'] == 'PRICE_FILTER':
                min_price, max_price, tick_size = float(binance_filter['minPrice']), float(binance_filter['maxPrice']), float(binance_filter['tickSize'])
        return min_qty, max_qty, step_size, min_price, max_price, tick_size

    def get_trade(self, trade_id=None, limit=None):
        return self.client.get_my_trades(symbol=SYMBOL, fromId=trade_id, limit=limit)

    def get_last_trade(self):
        return self.get_trade(limit=1)[0]


BINANCE = Binance()


