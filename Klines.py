from datetime import datetime
from Binance import BINANCE
from SqueezeMomentumIndicator import SqueezeMomentumIndicator
from Indicator import *
from Config import SYMBOL, INTERVAL

class Klines:
    def __init__(self):
        self.klines = pd.DataFrame()

    def load(self,):
        self._download()
        self.klines = self.klines.set_index('Time')
        self._caulculate()
        self.klines.dropna(inplace=True)


    def getKlines(self):
        return self.klines

    def _download(self):
        colums, times = ['Time','Open','High','Low','Close','Volume','ignore','ignore','ignore','ignore','ignore','ignore'], list()
        self.klines = pd.DataFrame(BINANCE.get_k_lines(symbol=SYMBOL,interval=INTERVAL,limit=41),columns=colums)
        self.klines['times'] = self.klines['Time']
        [times.append(datetime.fromtimestamp(int(str(time))/1000).strftime('%H:%M %d-%m-%Y')) for time in self.klines['Time']]
        self.klines['Time'] = times
        self.klines = self.klines.drop(['ignore','ignore','ignore','ignore','ignore','ignore'], axis=1)
        self.klines['mean'] = self.klines['Close'].rolling(window=20).mean()
        self.klines[['Open','High','Low','Close','Volume', 'mean']] = self.klines[['Open','High','Low','Close','Volume', 'mean']].astype(float)

    def _caulculate(self):
        self.klines['sm'] = SqueezeMomentumIndicator(self.klines)
        self.klines['adx'] = adxIndicator(self.klines)
        self.klines['sma'] = smaIndicator(self.klines,10)
