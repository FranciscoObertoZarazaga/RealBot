import numpy as np

def isSqueeze(df, length=20, mult = 2, length_KC = 20, mult_KC = 1.5):
    df = df.copy()
    # calculate Bollinger Bands
    # moving average
    m_avg = df['Close'].rolling(window=length).mean()
    # standard deviation
    m_std = df['Close'].rolling(window=length).std(ddof=0)
    # upper Bollinger Bands
    df['upper_BB'] = m_avg + mult * m_std
    # lower Bollinger Bands
    df['lower_BB'] = m_avg - mult * m_std

    # calculate Keltner Channel
    # first we need to calculate True Range
    df['tr0'] = abs(df["High"] - df["Low"])
    df['tr1'] = abs(df["High"] - df["Close"].shift())
    df['tr2'] = abs(df["Low"] - df["Close"].shift())
    df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
    # moving average of the TR
    range_ma = df['tr'].rolling(window=length_KC).mean()
    # upper Keltner Channel
    df['upper_KC'] = m_avg + range_ma * mult_KC
    # lower Keltner Channel
    df['lower_KC'] = m_avg - range_ma * mult_KC

    # check for 'squeeze'
    df['squeeze_on'] = (df['lower_BB'] > df['lower_KC']) & (df['upper_BB'] < df['upper_KC'])
    df['squeeze_off'] = (df['lower_BB'] < df['lower_KC']) & (df['upper_BB'] > df['upper_KC'])
    return df['squeeze_on']

def SqueezeMomentumIndicator(df, length = 20, length_KC = 20):
    df = df.copy()
    # calculate momentum value
    highest = df['High'].rolling(window = length_KC).max()
    lowest = df['Low'].rolling(window = length_KC).min()
    m_avg = df['Close'].rolling(window=length).mean()
    m1 = (highest + lowest) / 2
    df['value'] = (df['Close'] - (m1 + m_avg)/2)
    fit_y = np.array(range(0,length_KC))
    df['value'] = df['value'].rolling(window = length_KC).apply(lambda x : np.polyfit(fit_y, x, 1)[0] * (length_KC-1) + np.polyfit(fit_y, x, 1)[1], raw=True)
    return df['value']

'''
def squeezeMomentumIndicator(df, periodo=20):
    aux = df.copy()
    aux['lower'] = aux['Low'].rolling(window=periodo).min()
    aux['higher'] = aux['High'].rolling(window=periodo).max()
    aux['avg1'] = aux[["lower","higher"]].mean(axis=1)
    aux['avg2'] = aux[['mean','avg1']].mean(axis=1)
    aux['difference'] = pd.to_numeric(aux['Close']) - aux['avg2']
    n = pd.DataFrame()
    n['range'] = range(1,periodo+1)
    aux['xy'] = sumxy(aux['difference'],n['range'], periodo)
    n['x2'] = n['range'] ** 2
    aux['b'] = (periodo * aux['xy'] - aux['difference'].rolling(window=periodo).sum() * sum(n['range'])) / (periodo * sum(n['x2']) - sum(n['range']) ** 2)
    aux['a'] = (aux['difference'].rolling(window=periodo).sum() - aux['b'] * sum(n['range'])) / periodo
    aux['squeeze'] = aux['a'] + aux['b'] * (periodo - 1)
    return aux['squeeze']

def sumxy(x, y, periodo):
    sumxy = []
    [sumxy.append(None) for _ in range(periodo-1)]
    for i in range(periodo,len(x)+1):
        suma = []
        for j in range(periodo):
            suma.append(x[j + i - periodo] * y[j])
        resultado = 0
        for v in suma:
            resultado += 0 if pd.isna(v) else v
        sumxy.append(resultado)
    return sumxy
'''
