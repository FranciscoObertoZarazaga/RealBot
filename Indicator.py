from ta.trend import *
from ta.momentum import *


def adx_indicator(kline, period=14):
    return ADXIndicator(kline['High'], kline['Low'], kline['Close'], period).adx()


def sma_indicator(kline, period=50):
    return SMAIndicator(kline['Close'], period).sma_indicator()


def rsi_indicator(kline, period=14):
    return rsi(kline['Close'], period, False)
