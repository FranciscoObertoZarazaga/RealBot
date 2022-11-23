import pandas as pd
from Binance import Binance
from datetime import datetime
from Config import CONFIG

class Wallet:

    def __init__(self):
        self.binance = Binance()
        self.coins = self.binance.get_all_coins()
        self.wallet = dict(zip(self.coins, [0] * len(self.coins)))
        self.reward = 0
        self.initial_amount = 100
        self.addUSDT(self.initial_amount)
        self.buy_amount = 0
        self.buy_price = 0
        self.buy_time = None
        self.loss = 0
        self.trades = pd.DataFrame(columns=['final','inicial','reward'])
        self.limit_price = None

    def pay(self, price, time, coin, percentage=1, fiat='USDT'):
        assert self.isPayable(fiat)
        amount = self.getAmount(fiat) * percentage
        self.buy_amount = amount if fiat == 'USDT' else amount * self.binance.get_mean(f'{fiat}USDT')
        self.buy_price = price
        self.addAmount(coin, (amount * 0.999) / self.buy_price)
        self.addAmount(fiat, -amount)
        self.buy_time = time

    def collect(self, price, time, coin):
        assert self.isPositive(coin)
        sell_price = price
        reward = self.getAmount(coin) * sell_price * 0.999 - self.buy_amount
        self.addUSDT(reward + self.buy_amount)
        self.reward += reward
        self.loss += reward if reward < 0 else 0
        trade = {'final': self.getUSDT(),
                 'inicial': self.buy_amount,
                 'reward': reward,
                 'buy_price': self.buy_price,
                 'sell_price': price,
                 'buy_time': self.buy_time,
                 'sell_time': time,
                 'coin': coin}
        self.trades = self.trades.append(trade, ignore_index=True, )
        self.setAmount(coin, 0)
        self.buy_amount = 0
        return self.reward

    def __str__(self):
        trades = self.trades.copy()
        trades['tasa'] = trades['final'] / trades['inicial'] - 1
        n_trades = len(trades['reward'])
        n_positive_trades = len(trades[trades['reward'] >= 0])
        n_negative_trades = n_trades - n_positive_trades
        positive_rate = trades[trades['tasa'] >= 0]['tasa'].mean() * 100
        negative_rate = trades[trades['tasa'] < 0]['tasa'].mean() * 100
        mean_rate = trades['tasa'].mean() * 100
        self.rendimiento = mean_rate * n_trades


        msg = '=' * 50 + '\n' + "{:^50}".format('RESULTADO') + '\n' + '=' * 50 + '\n'
        print(self.reward, self.loss)
        ganancia_bruta = self.reward + abs(self.loss)
        try:
            tasa_de_aciertos = 100 * (1 - abs(self.loss) / (abs(self.loss) * 2 + self.reward))
        except ZeroDivisionError:
            return "NO SE REALIZÓ NINGÚN TRADE."
        tasa_de_ganancia = (self.getUSDT() / self.initial_amount)

        titulo = ['Monto Inicial',
                  'Monto Final',
                  'Crypto Final',
                  'Ganancia Bruta',
                  'Pérdida',
                  'Ganancia Neta',
                  'Acertabilidad',
                  'Multiplicador',
                  'N° de Trades',
                  'N° de Trades Positivos',
                  'N° de Trades Negativos',
                  'Tasa de Aciertos',
                  'Tasa Promedio',
                  'Tasa de Ganancia Promedio',
                  'Tasa de Pérdida Promedio',
                  'Rendimiendo']
        valor = [self.initial_amount,
                 self.getUSDT(),
                 self.getAmount('BTC'),
                 ganancia_bruta,
                 self.loss,
                 self.reward,
                 tasa_de_aciertos,
                 tasa_de_ganancia,
                 n_trades,
                 n_positive_trades,
                 n_negative_trades,
                 n_negative_trades/n_positive_trades,
                 mean_rate,
                 positive_rate,
                 negative_rate,
                 self.rendimiento]
        unidad = ['U$DT', 'U$DT', 'BTC', 'U$DT', 'U$DT', 'U$DT', '%', '', '', '', '', 'N/P', '%', '%', '%', '%']
        for i,t in enumerate(titulo):
            msg += f'{t:<30}{valor[i]: >10.2f} {unidad[i]: <5}\n'
            msg += '.' * 50 + '\n' if i < len(titulo) - 1 else '=' * 50 + '\n'
        return msg

    def get_reward(self):
        return self.reward

    def isPositive(self, coin):
        return self.getAmount(coin) > 0

    def isPayable(self, coin='USDT'):
        return self.isPositive(coin)

    def addAmount(self,coin, amount):
        self.wallet[coin] += amount

    def setAmount(self, coin, amount):
        self.wallet[coin] = amount

    def getAmount(self,coin):
        return self.wallet[coin]

    def addUSDT(self, amount):
        self.addAmount('USDT', amount)

    def setUSDT(self, amount):
        self.setAmount('USDT', amount)

    def getUSDT(self):
        return self.getAmount('USDT')

    def get_status(self):
        return self.getUSDT() == 0

    def set_buy_limit(self, price, disc=.999):
        self.limit_price = price*disc if self.limit_price is None else self.limit_price
        if price < self.limit_price:
            self.pay(price, datetime.now(), CONFIG.get_asset())
            self.limit_price = None
            print(self.wallet['USDT'], self.wallet['BTC'])

    def take_profit(self, price, disc=.999):
        self.limit_price = price*disc if self.limit_price is None else self.limit_price
        if price < self.limit_price:
            self.collect(price, datetime.now(), CONFIG.get_asset())
            self.limit_price = None
            print(self)


WALLET = Wallet()



