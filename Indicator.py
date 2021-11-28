from ta.trend import *
from ta.momentum import *
from ta.volatility import *

def adxIndicator(kline, periodo=14):
    return ADXIndicator(kline['High'],kline['Low'],kline['Close'],periodo).adx()

def smaIndicator(kline, periodo=50):
    return SMAIndicator(kline['Close'],periodo).sma_indicator()

def rsiIndicator(kline, periodo=14):
    return rsi(kline['Close'], periodo, False)

def bollingerBandsIndicator(kline, periodo=14):
    bb = BollingerBands(kline['Close'], periodo, 2, False)
    return bb.bollinger_hband(), bb.bollinger_mavg(), bb.bollinger_lband()
