from datetime import datetime
from Binance import BINANCE
from SqueezeMomentumIndicator import squeeze_momentum_indicator
from Indicator import *
from Config import SYMBOL


class Klines:
    def __init__(self):
        self.klines = pd.DataFrame()

    def load(self, interval, symbol=SYMBOL, limit=60, all=False):
        self._download(symbol, limit, interval, all=all)
        self.klines = self.klines.set_index('Time')
        #self.klines.index = pd.to_datetime(self.klines.index)
        self._calculate()
        self.klines.dropna(inplace=True)

    def get(self, interval):
        self.load(interval=interval)
        return self.klines

    def getAll(self, interval):
        self.load(interval=interval, all=True)
        return self.klines

    def _download(self, symbol, limit, interval, all):
        columns = [
            'Time',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume',
            'ignore',
            'ignore',
            'ignore',
            'ignore',
            'ignore',
            'ignore'
        ]
        times = list()
        if all:
            self.klines = pd.DataFrame(BINANCE.get_historical_k_lines(interval=interval, symbol=symbol, start_str='2015'), columns=columns)
        else:
            self.klines = pd.DataFrame(BINANCE.get_k_lines(limit=limit, interval=interval, symbol=symbol), columns=columns)
        self.klines['times'] = self.klines['Time']
        [times.append(datetime.fromtimestamp(int(str(time))/1000).strftime('%H:%M %d-%m-%Y')) for time in self.klines['Time']]
        self.klines['Time'] = times
        self.klines = self.klines.drop(['ignore', 'ignore', 'ignore', 'ignore', 'ignore', 'ignore'], axis=1)
        self.klines['mean'] = self.klines['Close'].rolling(window=20).mean()
        self.klines[['Open', 'High', 'Low', 'Close', 'Volume', 'mean']] = self.klines[['Open', 'High', 'Low', 'Close', 'Volume', 'mean']].astype(float)

    def _calculate(self):
        self.klines['sm'] = squeeze_momentum_indicator(self.klines)


KLINE = Klines()
