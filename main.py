import requests
import datetime
import pandas as pd
import ccxt
from datetime import datetime
import calendar
import numpy as np
from multiprocessing import Process


binance = ccxt.binance()

def min_ohlcv(dt, pair, limit):
    since = calendar.timegm(dt.utctimetuple())*1000
    ohlcv1 = binance.fetch_ohlcv(symbol=pair, timeframe='1m', since=since, limit=limit)
    ohlcv2 = binance.fetch_ohlcv(symbol=pair, timeframe='1m', since=since, limit=limit)
    ohlcv = ohlcv1 + ohlcv2
    return ohlcv

def ohlcv(dt, pair, period='1h'):
    ohlcv = []
    limit = 1000
    if period == '1m':
        limit = 720
    elif period == '1d':
        limit = 365
    elif period == '1h':
        limit = 24
    elif period == '5m':
        limit = 288
    for i in dt:
        start_dt = datetime.strptime(i, "%Y%m%d")
        since = calendar.timegm(start_dt.utctimetuple())*1000
        if period == '1m':
            ohlcv.extend(min_ohlcv(start_dt, pair, limit))
        else:
            ohlcv.extend(binance.fetch_ohlcv(symbol=pair, timeframe=period, since=since, limit=limit))
    df = pd.DataFrame(ohlcv, columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Time'] = [datetime.fromtimestamp(float(time)/1000) for time in df['Time']]
    df['Open'] = df['Open'].astype(np.float64)
    df['High'] = df['High'].astype(np.float64)
    df['Low'] = df['Low'].astype(np.float64)
    df['Close'] = df['Close'].astype(np.float64)
    df['Volume'] = df['Volume'].astype(np.float64)
    df.set_index('Time', inplace=True)
    return df


def main():
    Process(target=get_data(), daemon=True).start()
    input("")

def get_data():
    day = str(datetime.today()).split('-')
    today = str(day[0] + day[1] + day[2])[:8]
    print(today)
    while True:
        ohkcv_list = ohlcv([today, today], pair='XRP/USDT', period='1h')
        max_price = ohkcv_list['High'][len(ohkcv_list) - 1]
        key = "https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT"
        data = requests.get(key)
        data = data.json()
        current_price = float(data['price'])
        if current_price - max_price < 0 and abs(current_price - max_price) > max_price * 0.01:
            print(f"Внимание, цена {current_price} упала на 1% от максимальной: {max_price}")
        else:
            print(f"Цена {data['symbol']}: {current_price}, максимальная цена за последний час: {max_price}")


if __name__ == '__main__':
    main()




