from Config import IS_REAL_TRADER
from DataBase import DATABASE
from Binance import Binance
from Trades import Trades
from Results import Results
import pandas as pd


class Trader:
    def __init__(self, trader_id, name, api_key, secret_key):
        self.id = trader_id
        self.name = name
        self.binance = Binance(api_key=api_key, secret_key=secret_key)
        self.trades = Trades(self.binance, self.id)

    def buy(self, fiat, coin):
        if IS_REAL_TRADER:
            if self.binance.buy(fiat, coin):
                self.trades.set_trades()

    def sell(self, fiat, coin):
        if IS_REAL_TRADER:
            if self.binance.sell(fiat, coin):
                self.trades.set_trades()

    def set_stop_loss(self, price):
        self.binance.stop_loss(price)

    def set_buy_order(self, price):
        self.binance.buy_order(price)

    def get_results(self):
        dataframe = self.trades.trades
        results = Results(dataframe)
        return str(results)

    def get_last_trade(self):
        return self.binance.get_last_trade()


def get_all_traders():
    data = DATABASE.select('trader')
    traders = list()
    for trader in data:
        trader_id = trader[0]
        name = trader[1].strip()
        api_key = trader[2].strip()
        secret_key = trader[3].strip()
        traders.append(Trader(trader_id=trader_id, name=name, api_key=api_key, secret_key=secret_key))
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
