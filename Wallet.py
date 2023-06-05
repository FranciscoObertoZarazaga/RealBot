import json

import pandas as pd
from Binance import BINANCE
from datetime import datetime
from Config import FIAT, ASSET
from json import dumps, dump, load

COINS = {FIAT: 0, ASSET: 0}
TRADES = pd.DataFrame()


class Wallet:
    def __init__(self):
        self.wallet = None
        self.totalReward = None
        self.initial_amount = None
        self.buyAmount = None
        self.buyPrice = None
        self.buy_time = None
        self.totalLoss = None
        self.limit = None
        self.load()

    def constructor(self, wallet, reward, initial_amount, buy_amount, buy_price, buy_time, loss, limit_price):
        self.wallet = wallet
        self.totalReward = reward
        self.initial_amount = initial_amount
        self.buyAmount = buy_amount
        self.buyPrice = buy_price
        self.buy_time = buy_time
        self.totalLoss = loss
        self.limit = limit_price

    def pay(self, price):
        fiat, asset = FIAT, ASSET
        assert self.isPositive(fiat)
        self.buyAmount = self.getAmount(fiat)
        self.buyPrice = price
        self.addAmount(asset, (self.buyAmount * 0.999) / self.buyPrice)
        self.setAmount(fiat, 0)
        self.buy_time = str(datetime.now())
        self.save()
        print(FIAT, self.getAmount("USDT"), ASSET, self.getAmount("BTC"))

    def collect(self, price):
        fiat, asset = FIAT, ASSET
        assert self.isPositive(asset)
        sell_price = price
        reward = self.getAmount(asset) * sell_price * 0.999 - self.buyAmount
        self.addAmount(fiat, reward + self.buyAmount)
        self.totalReward += reward
        self.totalLoss += reward if reward < 0 else 0
        trade = self.getTrade(reward, sell_price)
        self.add(trade)
        self.setAmount(asset, 0)

    def __str__(self):
        trades = TRADES.copy()
        trades['tasa'] = trades['final'] / trades['inicial'] - 1
        n_trades = len(trades['reward'])
        n_positive_trades = len(trades[trades['reward'] >= 0])
        n_negative_trades = n_trades - n_positive_trades
        positive_rate = trades[trades['tasa'] >= 0]['tasa'].mean() * 100
        negative_rate = trades[trades['tasa'] < 0]['tasa'].mean() * 100
        mean_rate = trades['tasa'].mean() * 100
        self.rendimiento = mean_rate * n_trades

        msg = '=' * 50 + '\n' + "{:^50}".format('RESULTADO') + '\n' + '=' * 50 + '\n'

        ganancia_bruta = self.totalReward + abs(self.totalLoss)
        try:
            tasa_de_aciertos = 100 * (1 - abs(self.totalLoss) / (abs(self.totalLoss) * 2 + self.totalReward))
        except ZeroDivisionError:
            return "NO SE REALIZÓ NINGÚN TRADE."
        tasa_de_ganancia = (self.getAmount(FIAT) / self.initial_amount)

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
                 self.getAmount(FIAT),
                 self.getAmount(ASSET),
                 ganancia_bruta,
                 self.totalLoss,
                 self.totalReward,
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
        unidad = [FIAT, FIAT, ASSET, FIAT, FIAT, FIAT, '%', '', '', '', '', 'N/P', '%', '%', '%', '%']
        for i, t in enumerate(titulo):
            msg += f'{t:<30}{valor[i]: >10.2f} {unidad[i]: <5}\n'
            msg += '.' * 50 + '\n' if i < len(titulo) - 1 else '=' * 50 + '\n'

        return msg

    def getTotalReward(self):
        return self.totalReward

    def isPositive(self, coin):
        return self.getAmount(coin) > 0

    def addAmount(self, coin, amount):
        self.wallet[coin] += amount

    def setAmount(self, coin, amount):
        self.wallet[coin] = amount

    def getAmount(self, coin):
        return self.wallet[coin]

    def getStatus(self):
        return self.getAmount(FIAT) == 0

    def setLimit(self, price, disc):
        self.limit = price * disc

    def update(self, price):
        if self.limit is not None:
            if price < self.limit:
                self.collect(price)
                self.limit = None

    def add(self, trade):
        global TRADES
        trade = pd.DataFrame(trade)
        TRADES = pd.concat([TRADES, trade], ignore_index=True)
        self.save()

    def save(self):
        global TRADES
        TRADES.to_csv('trades.csv')
        file = open("wallet.json", "w")
        dump(dumps(self.__dict__), file, indent=6)
        file.close()

    def load(self):
        global TRADES
        try:
            TRADES = pd.read_csv('trades.csv', index_col=0)
            file = open("wallet.json", "r")
            wallet = json.loads(load(file))
            file.close()
            self.constructor(
                wallet['wallet'],
                wallet['totalReward'],
                wallet['initial_amount'],
                wallet['buyAmount'],
                wallet['buyPrice'],
                wallet['buy_time'],
                wallet['totalLoss'],
                wallet['limit']
            )
        except FileNotFoundError as e:
            TRADES = pd.DataFrame(columns=['final', 'inicial', 'reward'])
            self.constructor(dict(zip(COINS, [0] * len(COINS))), 0, 100, 0, 0, None, 0, None)
            self.addAmount(FIAT, self.initial_amount)

    def getTrade(self, reward, sell_price):
        return {
            'final': self.getAmount(FIAT),
            'inicial': self.buyAmount,
            'reward': reward,
            'buy_price': self.buyPrice,
            'sell_price': sell_price,
            'buy_time': self.buy_time,
            'sell_time': str(datetime.now()),
            'coin': ASSET
        }


WALLET = Wallet()
