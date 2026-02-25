print("Bot started")
print("TOKEN:", TOKEN)
import requests
import pandas as pd
import ta
import os
from telegram import Bot

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)

CHAT_ID = None


# دریافت chat id از آخرین پیام
def get_chat_id():
    global CHAT_ID

    updates = bot.get_updates()

    if not updates:
        return

    last = updates[-1]

    if last.message:
        CHAT_ID = last.message.chat.id


# دریافت داده کندل 15 دقیقه
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


# تحلیل حرفه‌ای
def analyze():

    df = get_data()

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    price = close.iloc[-1]

    # Indicators
    rsi = ta.momentum.RSIIndicator(close, 14).rsi().iloc[-1]

    ma20 = ta.trend.SMAIndicator(close, 20).sma_indicator().iloc[-1]

    macd = ta.trend.MACD(close)
    macd_val = macd.macd().iloc[-1]
    signal_line = macd.macd_signal().iloc[-1]

    # Support Resistance
    support = low.tail(50).min()
    resistance = high.tail(50).max()

    # Volume
    avg_volume = volume.mean()
    volume_spike = volume.iloc[-1] > avg_volume * 1.3

    # Pullback detection
    pullback = price > ma20 and rsi < 55

    # Score system
    pump_score = 0
    dump_score = 0

    if rsi > 65: pump_score += 1
    if rsi < 35: dump_score += 1

    if price > ma20: pump_score += 1
    else: dump_score += 1

    if macd_val > signal_line: pump_score += 1
    else: dump_score += 1

    if volume_spike: pump_score += 1

    # Prediction
    prediction = "Market Neutral"
    leverage = "No Trade"

    if pump_score >= 3:
        prediction = "🚀 احتمال پامپ 15 دقیقه آینده"
        leverage = "Leverage پیشنهادی: 2x - 3x کم ریسک"

    if dump_score >= 3:
        prediction = "📉 احتمال دامپ 15 دقیقه آینده"
        leverage = "Leverage پیشنهادی: 2x - 3x کم ریسک"

    advice = "مدیریت سرمایه فراموش نشود. ورود پله‌ای بهتر است."

    message = f"""
📊 BTC Futures 15m Analysis

Price: {price}
RSI: {round(rsi,2)}
MA20: {round(ma20,2)}
MACD: {round(macd_val,2)}
Signal: {round(signal_line,2)}

Support: {round(support,2)}
Resistance: {round(resistance,2)}

{prediction}
{leverage}

🧠 AI Advice:
{advice}
"""

    if CHAT_ID:
        bot.send_message(CHAT_ID, message)


# اجرا
if __name__ == "__main__":
    get_chat_id()
    analyze()
