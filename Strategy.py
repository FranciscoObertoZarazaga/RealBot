def squeeze_strategy(df, n=-1):
    sm = df['sm']
    is_min = sm[n] > sm[n - 1] and sm[n - 2] > sm[n - 1]
    is_max = sm[n] < sm[n - 1] and sm[n - 2] < sm[n - 1]
    if is_min:
        return 1
    if is_max:
        return -1
    return 0
