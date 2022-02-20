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
