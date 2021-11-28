from Binance import *
from Wallet import *

class Trader:

    def __init__(self,symbol, is_real_trader):
        self.wallet = RealWallet(symbol) if is_real_trader else Wallet(symbol)
        self.binance = Binance()
        self.symbol = symbol

    def buy(self):
        if self.wallet.isPayable():
            self.wallet.pay()


    def sell(self):
        if self.wallet.isCollectible():
            reward = self.wallet.collect()
            self.indoor = False

    def wait(self):
        time.sleep(10)

    def switch(self):
        try:
            return self.buy()
        except:
            return self.sell()

    def __str__(self):
        return str(self.wallet)



















