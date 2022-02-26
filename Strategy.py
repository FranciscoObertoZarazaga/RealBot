def squeeze_strategy(df, n=-1):
    sm = df['sm']
    is_min = sm[n] > sm[n - 1] and sm[n - 2] > sm[n - 1]
    is_max = sm[n] < sm[n - 1] and sm[n - 2] < sm[n - 1]
    if is_min:
        return 1
    if is_max:
        return -1
    return 0


def squeeze_buster_strategy(df, n=-1):
    sm = df['sm']
    up = sm[n] > sm[n - 1]
    if up:
        return 1
    return -1

def get_volatility(df):
    atr = df['atr'][-1]
    price = df['Close'][-1]
    return atr * 100 / price

def dynamic_stop_loss(status, price, last_price):
    if status:
        if last_price is None:
            return -1
        if price > last_price:
            return -1
    else:
        if last_price is None:
            return 1
        if price < last_price:
            return 1
    return 0

def NovechentaStrategy(df, n=-1):
    adx = df['adx']
    sm = df['sm']

    #Si el adx alcanza un mínimo o un máximo
    if (adx[n] < adx[n - 1] and adx[n - 2] < adx[n - 1]) or (adx[n] > adx[n - 1] and adx[n - 2] > adx[n - 1]):
        #Si el monitor es bajista con direccion alcista
        if sm[n] > sm[n - 1] and sm[n] < 0:
            #Compro
            return 1
        #Si el monitor es alcista con direccion bajista
        if sm[n] < sm[n - 1] and sm[n] > 0:
            #Vendo
            return -1
    return 0
