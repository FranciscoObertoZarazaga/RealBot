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

def get_buy_price():
    last_trade = TRADERS[0].get_last_trade()
    if last_trade is None:
        return 0
    if last_trade['isBuyer']:
        return float(last_trade['price'])
    return 0

def assert_price(price):
    msg = f'(best_price or buy_price)=({price}) must be mayor than 0'
    assert price > 0, msg

def verify_price(price):
    try:
        assert_price(price)
        return price
    except AssertionError:
        return get_buy_price()



