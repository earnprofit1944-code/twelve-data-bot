import os
import time
import requests

# Telegram Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

def send_tg(msg):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        try:
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            print(f"Telegram Send Error: {e}")

def fetch_price_safe(symbol):
    if not TWELVE_DATA_API_KEY:
        print("API Key Missing")
        return None
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        if "price" in res:
            return float(res["price"])
        else:
            print(f"Error fetching {symbol}: {res}")
            return None
    except Exception as e:
        print(f"Request Error for {symbol}: {e}")
        return None

# Alerts Setup
all_scripts = {
    "EUR/USD": {"Up": 1.1000, "Down": 1.0500}
}

triggered = set()

for sym, levels in all_scripts.items():
    live_price = fetch_price_safe(sym)
    if live_price:
        for lvl, target_price in levels.items():
            key = f"{sym}_{lvl}"
            if key not in triggered:
                if ("Up" in lvl and live_price >= target_price) or ("Down" in lvl and live_price <= target_price):
                    send_tg(f"🚨 {sym} | {lvl}: {target_price} | Live: {live_price}")
                    triggered.add(key)

print("Check completed successfully.")
