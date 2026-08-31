import os
import time
import requests

# ------------------------------------------------------------------
# Environment Variables & Credentials
# ------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

# ------------------------------------------------------------------
# Telegram Dispatch Helper
# ------------------------------------------------------------------
def send_tg(msg):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        try:
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            print(f"Telegram Send Error: {e}")

# ------------------------------------------------------------------
# Twelve Data Fetching Helper
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# Main Alert Checker Strategy
# ------------------------------------------------------------------
def main():
    # Define targets and trading symbols
    # Format: "SYMBOL": [("Level Name", Target Price), ...]
    targets = {
        "EUR/JPY": [
            ("Down B1_3", 184.93),
            ("Down E1", 185.20),
            ("Down E2", 184.80)
        ],
        "ETH/USD": [
            ("Down B1_3", 2500.00),
            ("Down E1", 2516.00)
        ]
    }

    triggered = set()

    for sym, levels in targets.items():
        live_price = fetch_price_safe(sym)
        if live_price is None:
            continue

        for lvl, target_price in levels:
            key = f"{sym}_{lvl}"
            if key in triggered:
                continue

            # Evaluate signal logic based on level direction
            is_up_signal = "Up" in lvl and live_price >= target_price
            is_down_signal = "Down" in lvl and live_price <= target_price

            if is_up_signal or is_down_signal:
                alert_msg = f"🚨 {sym} | {lvl}: {target_price} | Live: {live_price}"
                send_tg(alert_msg)
                triggered.add(key)

        # Sleep briefly between calls to prevent rate-limit bans
        time.sleep(1)

    print("Check completed successfully.")

if __name__ == "__main__":
    main()
