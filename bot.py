import requests
import pandas as pd
import numpy as np
import ta
from telegram import Bot
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = None  # بعدا ست می‌کنیم

bot = Bot(token=TOKEN)

def get_chat_id():
    global CHAT_ID
    updates = bot.get_updates()
    if updates:
        CHAT_ID = updates[-1].message.chat.id

def get_data():
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
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df

def analyze():
    df = get_data()

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    price = close.iloc[-1]

    # RSI
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]

    # MA20
    ma20 = ta.trend.SMAIndicator(close, window=20).sma_indicator().iloc[-1]

    # MACD
    macd = ta.trend.MACD(close)
    macd_val = macd.macd().iloc[-1]
    signal_line = macd.macd_signal().iloc[-1]

    # Support & Resistance
    resistance = high.max()
    support = low.min()

    # Volume Spike
    avg_volume = volume.mean()
    volume_spike = volume.iloc[-1] > avg_volume * 1.3

    # Signal Logic
    pump_score = 0
    dump_score = 0

    if rsi > 65: pump_score += 1
    if rsi < 35: dump_score += 1
    if price > ma20: pump_score += 1
    else: dump_score += 1
    if macd_val > signal_line: pump_score += 1
    else: dump_score += 1
    if volume_spike: pump_score += 1

    prediction = "Neutral"
    leverage = "No Trade"

    if pump_score >= 3:
        prediction = "🚀 احتمالا پامپ در 15 دقیقه آینده"
        leverage = "Leverage پیشنهادی: 3x کم ریسک"
    elif dump_score >= 3:
        prediction = "📉 احتمالا دامپ در 15 دقیقه آینده"
        leverage = "Leverage پیشنهادی: 3x کم ریسک"

    advice = "بازار نوسانی است. مدیریت سرمایه رعایت شود."

    message = f"""
📊 BTC Futures 15m Analysis

Price: {price}
RSI: {round(rsi,2)}
MA20: {round(ma20,2)}
MACD: {round(macd_val,2)}
Signal Line: {round(signal_line,2)}

Resistance: {round(resistance,2)}
Support: {round(support,2)}

{prediction}
{leverage}

🧠 AI Insight:
{advice}
"""

    if CHAT_ID:
        bot.send_message(chat_id=CHAT_ID, text=message)

if __name__ == "__main__":
    get_chat_id()
    analyze()
