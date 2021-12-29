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
                self.save_trade()

    def sell(self):
        if IS_REAL_TRADER:
            if self.binance.sell(SYMBOL):
                self.save_trade()

    def save_trade(self):
        last_trade = self.binance.get_last_trade(SYMBOL)
        trade_id = last_trade['id']
        self.trades.add_trade(self.id, trade_id)

    def get_results(self):
        dataframe = self.trades.get_trades_dataframe()
        results = Results(dataframe)
        return str(results)

    def wait(self):
        sleep(10)


class Trades:
    def __init__(self, binance, trader_id):
        self.trader_id = trader_id
        self.binance = binance
        self.trades = self._get_trades() if trader_id is not None else list()

    def add_trade(self, trader_id, trade_id):
        data = self.binance.get_trade_with_id(symbol=SYMBOL, trade_id=trade_id)
        price, quote_qty, time, is_buyer = (
            float(data['price']),
            float(data['quoteQty']),
            int(data['time']),
            data['isBuyer']
        )
        DATABASE.insert(
            'trades',
            'trader_id,trade_id,symbol,price,quote_qty,time,is_buyer',
            f"{trader_id},{trade_id},'{SYMBOL}',{price},{quote_qty},{time},{is_buyer}"
        )
        #self.trades = self._get_trades()
        self.trades.append(self.Trade([None, trader_id, trade_id, SYMBOL, price, quote_qty, time, is_buyer], self.binance))

    def _get_trades(self):
        trades = list()
        data = DATABASE.select_with('trades', 'trader_id', self.trader_id)
        for trade in data:
            trades.append(self.Trade(trade, self.binance))
        return trades

    def get_trades(self):
        return self.trades

    def get_trade_id(self):
        ids = []
        for trade in self.trades:
            ids.append(trade.trade_id)
        return ids

    def _get_artificial_trade(self, key, trades):
        mean, total, time = 0, 0, None
        for trade in trades[key]:
            total += trade.quote_qty
            time = trade.time
        for trade in trades[key]:
            mean += trade.price * (trade.quote_qty / total)
        return mean, total, time

    def _trim_trades(self, trades):
        for i, trade in enumerate(trades):
            if not trade.is_buyer:
                trades.remove(trade)
            else:
                break

    def _join_trades(self, all_trades):
        for trade in all_trades:
            if len(trade['buy']) > 1:
                mean, qty, time = self._get_artificial_trade('buy', trade)
                artificial_trade = self.Trade([None, self.trader_id, None, SYMBOL, mean, qty, time, True], self.binance)
                trade['buy'] = artificial_trade
            if len(trade['sell']) > 1:
                mean, qty, time = self._get_artificial_trade('sell', trade)
                artificial_trade = self.Trade([None, self.trader_id, None, SYMBOL, mean, qty, time, False], self.binance)
                trade['sell'] = artificial_trade
            if isinstance(trade['buy'], list):
                trade['buy'] = trade['buy'][0]
            if isinstance(trade['sell'], list):
                trade['sell'] = trade['sell'][0]

    def _make_pairs(self):
        trades = self.trades.copy()
        self._trim_trades(trades)
        buy, sell = [], []
        all_trades = []
        for trade in trades:
            if trade.is_buyer:
                if buy and sell:
                    all_trades.append({'buy': buy, 'sell': sell})
                    buy, sell = [], []
                buy.append(trade)
            else:
                sell.append(trade)
        return all_trades

    def get_trades_dataframe(self):
        data = pd.DataFrame()
        all_trades = self._make_pairs()
        self._join_trades(all_trades)
        for trade in all_trades:
            row = {
                'buy_amount': trade['buy'].quote_qty,
                'sell_amount': trade['sell'].quote_qty,
                'buy_price': trade['buy'].price,
                'sell_price': trade['sell'].price,
                'buy_time': trade['buy'].get_time(),
                'sell_time': trade['sell'].get_time(),
                'symbol': trade['buy'].symbol
            }
            data = data.append(row, ignore_index=True)
        return data

    def sort(self):
        self.trades.sort(key=self._get_trade_time)

    def _get_trade_time(self, trade):
        return trade.time

    class Trade:
        def __init__(self, trade, binance):
            self.binance = binance
            self.trader_id = trade[1]
            self.trade_id = trade[2]
            self.symbol = trade[3].strip()
            self.price = trade[4]
            self.quote_qty = trade[5]
            self.time = trade[6]
            self.is_buyer = trade[7]

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


"""
def get_results():
    array = list()
    for trader in TRADERS:
        data = trader.trades.get_trades_dataframe()
        results = str(Results(data))
        msg = '#' * 25 + f'\nTrader: {trader.name.upper()}\n'
        msg += results
        msg += '\n' * 5
        array.append(msg)
    return array
"""


def get_results():
    aux_trades = Trades(None, None)
    for trader in TRADERS:
        aux_trades.trades = aux_trades.trades + trader.trades.trades
    aux_trades.sort()
    dataframe = aux_trades.get_trades_dataframe()
    results = Results(dataframe)
    return str(results)


TRADERS = get_all_traders()


















