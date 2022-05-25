import pandas as pd
from datetime import datetime


class Trades:
    def __init__(self, binance, trader_id):
        self.trader_id = trader_id
        self.binance = binance
        self.trades = self._get_trades()

    def _get_trades(self):
        trades = self.binance.get_trade()
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

    @staticmethod
    def _get_trades_dataframe(trades):
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
            trade_dataframe = pd.DataFrame(row, columns=row.keys(), index=[0])
            data = pd.concat([data, trade_dataframe], ignore_index=True)
        return data

    @staticmethod
    def _get_trade_time(trade):
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
