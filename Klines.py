from datetime import datetime
from Binance import BINANCE
from SqueezeMomentumIndicator import squeeze_momentum_indicator
from Indicator import *


class Klines:
    def __init__(self):
        self.klines = pd.DataFrame()

    def load(self):
        self._download()
        self.klines = self.klines.set_index('Time')
        self._calculate()
        self.klines.dropna(inplace=True)

    def get_klines(self):
        return self.klines

    def _download(self):
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
        self.klines = pd.DataFrame(BINANCE.get_k_lines(limit=41), columns=columns)
        self.klines['times'] = self.klines['Time']
        [times.append(datetime.fromtimestamp(int(str(time))/1000).strftime('%H:%M %d-%m-%Y')) for time in self.klines['Time']]
        self.klines['Time'] = times
        self.klines = self.klines.drop(['ignore', 'ignore', 'ignore', 'ignore', 'ignore', 'ignore'], axis=1)
        self.klines['mean'] = self.klines['Close'].rolling(window=20).mean()
        self.klines[['Open', 'High', 'Low', 'Close', 'Volume', 'mean']] = self.klines[['Open', 'High', 'Low', 'Close', 'Volume', 'mean']].astype(float)

    def _calculate(self):
        self.klines['sm'] = squeeze_momentum_indicator(self.klines)
        self.klines['adx'] = adx_indicator(self.klines)
        self.klines['sma'] = sma_indicator(self.klines, 10)
