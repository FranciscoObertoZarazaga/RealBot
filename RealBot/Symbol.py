from Klines import Klines
from Strategy import get_volatility
from Config import CONFIG

ASSETS = ['BTC', 'ETH', 'ADA', 'LTC', 'BNB', 'XRP', 'SOL', 'AVAX', 'DAI', 'DOGE']
kline = Klines()

def search_asset():
    volatilities = list()
    for asset in ASSETS:
        symbol = asset + CONFIG.get_fiat()
        kline.load(symbol, limit=41)
        data = kline.get_klines()
        volatility = get_volatility(data)
        volatilities.append(volatility)
    max_volatility = max(volatilities)
    index = volatilities.index(max_volatility)
    CONFIG.set_config(ASSETS[index])
