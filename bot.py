import requests
import pandas as pd
import ta

def get_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    data = requests.get(url).json()
    return data["bitcoin"]["usd"]

def get_data():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCUSDT",
        "interval": "15m",
        "limit": 50
    }

    data = requests.get(url, params=params).json()
    df = pd.DataFrame(data)

    df.columns = [
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ]

    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df

def analyze():
    df = get_data()
    close = df["close"]
    volume = df["volume"]

    price = get_price()

    rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]
    ma20 = ta.trend.SMAIndicator(close, window=20).sma_indicator().iloc[-1]

    macd = ta.trend.MACD(close)
    macd_value = macd.macd().iloc[-1]
    signal_line = macd.macd_signal().iloc[-1]

    avg_volume = volume.mean()
    volume_spike = volume.iloc[-1] > avg_volume * 1.3

    pump = (rsi > 70) and (price > ma20) and (macd_value > signal_line) and volume_spike
    dump = (rsi < 30) and (price < ma20) and (macd_value < signal_line) and volume_spike

    print("📊 BTC 15m Analysis")
    print("Price:", price)
    print("RSI:", rsi)
    print("MA20:", ma20)
    print("MACD:", macd_value)
    print("Signal Line:", signal_line)

    if pump:
        print("🚀 Pump احتمال زیاد (Buy)")
    elif dump:
        print("📉 Dump احتمال زیاد (Sell)")
    else:
        print("⚖ Market Neutral")

if __name__ == "__main__":
    analyze()
