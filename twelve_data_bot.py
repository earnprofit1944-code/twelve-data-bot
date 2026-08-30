import time
import requests
from twelvedata import TDClient

BOT_TOKEN = "8858225846:AAFmYHWJmtfMKIs9X2S_vrsmd8hhbVScxII"
CHAT_ID = "241549590"
TWELVE_DATA_KEY = "12e5987195384463a337c1703ac644fe"

td = TDClient(apikey=TWELVE_DATA_KEY)

all_scripts = {
    "XAU/USD": {
        "Up C1": 4621.00, "Up C2": 4647.00, "Up C3": 4673.00,
        "Down B1_3": 4569.00, "Down B2_3": 4543.00, "Down B3_3": 4517.00,
        "Up D1": 4610.60, "Up D5": 4673.00, "Down E1": 4579.40, "Down E5": 4517.00
    },
    "BTC/USD": {
        "Up C1": 80940.00, "Up C3": 82340.00,
        "Down B1_3": 79540.00, "Down B3_3": 78140.00
    },
    "ETH/USD": {
        "Up C1": 2580.00, "Up C3": 2660.00,
        "Down B1_3": 2500.00, "Down B3_3": 2420.00
    },
    "USD/JPY": {"Up C1": 159.97, "Down B1_3": 158.63},
    "GBP/JPY": {"Up C1": 217.17, "Down B1_3": 215.83},
    "EUR/JPY": {"Up C1": 186.27, "Down B1_3": 184.93},
    "AUD/JPY": {"Up C1": 115.27, "Down B1_3": 113.93},
    "CAD/JPY": {"Up C1": 115.57, "Down B1_3": 114.23}
}

def send_tg(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg})

def fetch_price_safe(symbol):
    try:
        res = td.price(symbol=symbol).as_json()
        if 'price' in res:
            return float(res['price'])
    except Exception as e:
        print(f"Error {symbol}: {e}")
    return None

triggered = set()

print("Initializing Bot (Safe Rate-Limit Mode)...")

# Initial Breach Filter
for sym in all_scripts.keys():
    price = fetch_price_safe(sym)
    if price:
        for lvl, target_price in all_scripts[sym].items():
            key = f"{sym}_{lvl}"
            if ("Up" in lvl and price >= target_price) or ("Down" in lvl and price <= target_price):
                triggered.add(key)
    time.sleep(10)  # Wait 10 seconds between each symbol startup check

send_tg("🤖 Twelve Data Live Bot Active (Rate-Limit Fixed)!")

# Loop through symbols with 12-second intervals
try:
    while True:
        for sym, levels in all_scripts.items():
            live_price = fetch_price_safe(sym)
            if live_price:
                for lvl, target_price in levels.items():
                    key = f"{sym}_{lvl}"
                    if key not in triggered:
                        if ("Up" in lvl and live_price >= target_price) or ("Down" in lvl and live_price <= target_price):
                            send_tg(f"🚨 {sym} | {lvl}: {target_price} | Live: {live_price}")
                            triggered.add(key)
            
            # Wait 12 seconds per call (Max 5 requests per minute -> Safely under 8/min limit)
            time.sleep(12)

except KeyboardInterrupt:
    print("Bot Stopped.")