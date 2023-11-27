from Binance import Binance
from Trades import Trades
from Results import Results
from Wallet import WALLET
from Config import IS_REAL_TRADER
from Config import PUBLIC_KEY, SECRET_KEY


class Trader:
    def __init__(self, api_key, secret_key):
        self.binance = Binance(api_key=api_key, secret_key=secret_key)
        self.trades = Trades(self.binance)

    def buy(self, price):
        if IS_REAL_TRADER:
            if self.binance.buy():
                self.trades.set_trades()
        else:
            WALLET.pay(price)

    def sell(self, price):
        if IS_REAL_TRADER:
            if self.binance.sell():
                self.trades.set_trades()
        else:
            WALLET.collect(price)

    def set_stop_loss(self, price, disc=.998):
        if IS_REAL_TRADER:
            self.binance.stop_loss(price)
        else:
            WALLET.setLimit(price, disc)

    def set_buy_order(self, price):
        if IS_REAL_TRADER:
            self.binance.buy_order(price)
        else:
            WALLET.setLimit(price)

    def set_buy_order_limit(self, price):
        if IS_REAL_TRADER:
            self.binance.order_buy_limit(price)
        else:
            WALLET.set_buy_limit(price)

    def get_results(self):
        dataframe = self.trades.trades
        results = Results(dataframe)
        return str(results)

    def get_last_trade(self):
        return self.binance.get_last_trade()

    def getStatus(self):
        if IS_REAL_TRADER:
            last_trade = self.get_last_trade()
            if last_trade is None:
                return False
            return last_trade['isBuyer']
        else:
            return WALLET.getStatus()

    def get_buy_price(self):
        last_trade = self.get_last_trade()
        if last_trade is None:
            return 0
        if last_trade['isBuyer']:
            return float(last_trade['price'])
        return 0

    @staticmethod
    def update(price):
        WALLET.update(price)


TRADER = Trader(PUBLIC_KEY, SECRET_KEY)
