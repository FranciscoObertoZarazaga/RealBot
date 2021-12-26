from Config import SYMBOL, IS_REAL_TRADER
from time import sleep
from DataBase import DATABASE
from Binance import Binance


class Trader:
    def __init__(self, id, name, api_key, secret_key):
        self.id = id
        self.name = name
        self.binance = Binance(api_key=api_key, secret_key=secret_key)

    def buy(self):
        if IS_REAL_TRADER:
            if self.binance.buy(SYMBOL):
                self.save_trade()

    def sell(self):
        if IS_REAL_TRADER:
            if self.binance.sell(SYMBOL):
                self.save_trade()

    def save_trade(self):
        last_trade = self.binance.get_last_trade(SYMBOL)
        trade_id = last_trade['id']
        TRADES.add_trade(self.id, trade_id)


    def wait(self):
        sleep(10)


def get_all_traders():
    data = DATABASE.select('trader')
    traders = list()
    for trader in data:
        id = trader[0]
        name = trader[1].strip()
        api_key = trader[2].strip()
        secret_key = trader[3].strip()
        traders.append(Trader(id=id, name=name, api_key=api_key, secret_key=secret_key))
    return traders


class Trades:
    def __init__(self):
        self.trades = self._get_trades()

    def add_trade(self, trader_id, trade_id):
        DATABASE.insert('trades', 'trader_id,trade_id,symbol', f"{trader_id},{trade_id},'{SYMBOL}'")
        self.trades = self._get_trades()

    def _get_trades(self):
        trades = list()
        data = DATABASE.select('trades')
        for trade in data:
            trades.append(self.Trade(trade))
        return trades

    def get_trades(self):
        return self.trades

    def get_trade_id(self):
        ids = []
        for trade in self.trades:
            ids.append(trade.trade_id)
        return ids

    class Trade:
        def __init__(self, trade):
            self.id, self.trader_id, self.trade_id, self.symbol = trade[0], trade[1], trade[2], trade[3].strip()




TRADERS = get_all_traders()
TRADES = Trades()

















