def WinStrategy(df, n=-1):
    adx = df['adx']
    sm = df['sm']
    sma = df['sma']
    price = df['Close']
    isMin = adx[n] > adx[n-1] and adx[n-2] > adx[n-1]
    isUp = price[n] > sma[n]
    isMagic = sm[n] > sm[n-1] or isUp

    if isMin:
        if adx[n-1] < 30:
            return 1 if isMagic else -1
    return 0


def SqueezeStrategy(df, n=-1):
    sm = df['sm']
    isMin = sm[n] > sm[n - 1] and sm[n - 2] > sm[n - 1]
    isMax = sm[n] < sm[n - 1] and sm[n - 2] < sm[n - 1]
    if isMin:
        return 1
    if isMax:
        return -1
    return 0

