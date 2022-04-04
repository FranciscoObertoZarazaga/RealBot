from Trader import TRADERS
from threading import Thread


def all_do(function):
    def wrap(*args, **kwargs):
        buy_threads = list()
        for trader in TRADERS:
            function(buy_threads, trader, *args, **kwargs)
        for thread in buy_threads:
            thread.start()
    return wrap


@all_do
def all_buy(buy_threads, trader):
    buy_threads.append(Thread(target=trader.buy))


@all_do
def all_sell(sell_threads, trader):
    sell_threads.append(Thread(target=trader.sell()))


@all_do
def all_set_stop_loss(threads, trader, price):
    threads.append(Thread(target=trader.set_stop_loss, args=[price]))


@all_do
def all_set_buy_order(threads, trader, price):
    threads.append(Thread(target=trader.set_buy_order, args=[price]))


def do(action):
    if action > 0:
        all_buy()
    if action < 0:
        all_sell()


def get_status():
    last_trade = TRADERS[0].get_last_trade()
    if last_trade is None:
        return False
    return last_trade['isBuyer']

