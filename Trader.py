from Binance import *
from Wallet import *

class Trader:

    def __init__(self,symbol, is_real_trader):
        self.wallet = RealWallet(symbol) if is_real_trader else Wallet(symbol)
        self.binance = Binance()
        self.symbol = symbol

    def buy(self):
        self.wallet.pay()


    def sell(self):
        self.wallet.collect()

    def wait(self):
        time.sleep(10)

    def __str__(self):
        return str(self.wallet)



















