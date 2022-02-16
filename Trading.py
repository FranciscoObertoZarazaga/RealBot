from Trader import TRADERS
from threading import Thread


def all_buy():
    buy_threads = list()
    for trader in TRADERS:
        buy_threads.append(Thread(target=trader.buy))
    for thread in buy_threads:
        thread.start()


def all_sell():
    sell_threads = list()
    for trader in TRADERS:
        sell_threads.append(Thread(target=trader.sell()))
    for thread in sell_threads:
        thread.start()


def all_set_stop_loss():
    sell_threads = list()
    for trader in TRADERS:
        sell_threads.append(Thread(target=trader.set_stop_loss()))
    for thread in sell_threads:
        thread.start()


def do(action):
    if action > 0:
        all_buy()
    if action < 0:
        all_sell()


def get_status():
    return TRADERS[0].get_last_trade()['isBuyer']