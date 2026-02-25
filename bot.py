import requests
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8742635438:AAHdSn7_N6UpQtQ-7W2PVHOh9h8Z5nZImtg"

# گرفتن داده بیت کوین
def get_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1"
    data = requests.get(url).json()
    prices = [x[1] for x in data["prices"]]
    df = pd.DataFrame(prices, columns=["price"])
    return df

# محاسبه RSI
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# محاسبه MACD
def calculate_macd(series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات تحلیلگر فعال است ✅\nبرای تحلیل بنویس /analyze")

# /analyze
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = get_data()

    rsi = calculate_rsi(df["price"])
    ma = df["price"].rolling(20).mean()
    macd, macd_signal = calculate_macd(df["price"])

    price = df["price"].iloc[-1]
    rsi_value = rsi.iloc[-1]
    ma_value = ma.iloc[-1]
    macd_value = macd.iloc[-1]
    macd_signal_value = macd_signal.iloc[-1]

    signal_text = "Neutral"

    if rsi_value < 30 and macd_value > macd_signal_value:
        signal_text = "Buy 📈"
    elif rsi_value > 70 and macd_value < macd_signal_value:
        signal_text = "Sell 📉"

    message = (
        f"📊 Bitcoin Analysis\n\n"
        f"Price: {price}\n"
        f"RSI: {rsi_value}\n"
        f"MA20: {ma_value}\n"
        f"MACD: {macd_value}\n"
        f"Signal Line: {macd_signal_value}\n\n"
        f"Final Signal: {signal_text}"
    )

    await update.message.reply_text(message)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()