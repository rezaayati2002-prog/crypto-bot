import requests
import pandas as pd
import ta
import time

symbol = "bitcoin"

def get_price():
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    return requests.get(url).json()[symbol]["usd"]

def get_candles():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCUSDT",
        "interval": "15m",
        "limit": 100
    }
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df

def analyze():
    df = get_candles()

    close = df["close"]
    volume = df["volume"]

    # RSI
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]

    # MA
    ma20 = ta.trend.SMAIndicator(close, window=20).sma_indicator().iloc[-1]

    # MACD
    macd = ta.trend.MACD(close)
    macd_value = macd.macd().iloc[-1]
    signal = macd.macd_signal().iloc[-1]

    price = get_price()

    # Volume Spike
    avg_volume = volume.mean()
    volume_signal = volume.iloc[-1] > avg_volume * 1.3

    # Pump / Dump Detection
    pump = rsi > 70 and price > ma20 and macd_value > signal and volume_signal
    dump = rsi < 30 and price < ma20 and macd_value < signal and volume_signal

    print("\n📊 BTC 15m Analysis")
    print(f"Price: {price}")
    print(f"RSI: {rsi}")
    print(f"MA20: {ma20}")
    print(f"MACD: {macd_value}")
    print(f"Signal Line: {signal}")

    if pump:
        print("🚀 Pump احتمال زیاد (Buy Signal)")
    elif dump:
        print("📉 Dump احتمال زیاد (Sell Signal)")
    else:
        print("⚖ Market Neutral")

if __name__ == "__main__":
    while True:
        analyze()
        time.sleep(300)
