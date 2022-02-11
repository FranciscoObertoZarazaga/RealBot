from Config import SYMBOL, IS_REAL_TRADER
from time import sleep
from DataBase import DATABASE
from Binance import Binance
from datetime import datetime
from Results import Results
import pandas as pd

class Trader:
    def __init__(self, id, name, api_key, secret_key):
        self.id = id
        self.name = name
        self.binance = Binance(api_key=api_key, secret_key=secret_key)
        self.trades = Trades(self.binance, self.id)

    def buy(self):
        if IS_REAL_TRADER:
            if self.binance.buy(SYMBOL):
                self.trades.set_trades()

    def sell(self):
        if IS_REAL_TRADER:
            if self.binance.sell(SYMBOL):
                self.trades.set_trades()

    def get_results(self):
        dataframe = self.trades.trades
        results = Results(dataframe)
        return str(results)

    def get_last_trade(self):
        return self.binance.get_last_trade(SYMBOL)


class Trades:
    def __init__(self, binance, trader_id):
        self.trader_id = trader_id
        self.binance = binance
        self.trades = self._get_trades()

    def _get_trades(self):
        trades = self.binance.get_trade(SYMBOL)
        trade_list = list()
        for trade in trades:
            trade_list.append(self.Trade(trade))
        trade_list.sort(key=self._get_trade_time)
        data = self._get_trades_dataframe(trade_list)
        return data

    def get_trades(self):
        return self.trades

    def set_trades(self):
        self.trades = self._get_trades()

    def _get_trades_dataframe(self, trades):
        data = pd.DataFrame()

        for trade in trades:
            row = {
                'id': trade.trade_id,
                'qty': trade.quote_qty,
                'price': trade.price,
                'is_buyer': trade.is_buyer,
                'time': trade.get_time(),
                'symbol': trade.symbol
            }
            data = data.append(row, ignore_index=True)
        return data

    def _get_trade_time(self, trade):
        return trade.time

    class Trade:
        def __init__(self, trade):
            self.trade_id = trade['id']
            self.symbol = trade['symbol']
            self.price = float(trade['price'])
            self.quote_qty = float(trade['quoteQty'])
            self.time = trade['time']
            self.is_buyer = trade['isBuyer']

        def get_time(self):
            return datetime.fromtimestamp(int(str(self.time)) / 1000)


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


def get_results():
    array = list()
    for trader in TRADERS:
        data = trader.trades.trades
        results = str(Results(data))
        msg = '#' * 25 + f'\nTrader: {trader.name.upper()}\n'
        msg += results
        msg += '\n' * 5
        array.append(msg)
    return array

def get_trades():
    dataframe = pd.DataFrame()
    for trader in TRADERS:
        dataframe = pd.concat([dataframe, trader.trades.trades], axis=0, ignore_index=True)
    path = 'trades.csv'
    dataframe.to_csv(path)
    return path

TRADERS = get_all_traders()


















