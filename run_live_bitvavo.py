# run_live_bitvavo.py
import os
import time
import pandas as pd
from dotenv import load_dotenv
from bot.broker_bitvavo import BitvavoBroker
from telegram_notifier import TelegramNotifier
from email_notifier import EmailNotifier

# Load .env
load_dotenv()

broker = BitvavoBroker()
telegram = TelegramNotifier()
email = EmailNotifier()

def notify(subject: str, body: str):
    """Send both Telegram and Email notifications."""
    telegram.send(f"{subject}\n{body}")
    email.send(subject, body)

def compute_signal(candles):
    df = pd.DataFrame(candles)
    if len(df) < 50:
        return 0
    df["sma_fast"] = df["close"].rolling(10).mean()
    df["sma_slow"] = df["close"].rolling(40).mean()
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if prev["sma_fast"] <= prev["sma_slow"] and last["sma_fast"] > last["sma_slow"]:
        return 1
    if prev["sma_fast"] >= prev["sma_slow"] and last["sma_fast"] < last["sma_slow"]:
        return -1
    return 0

if __name__ == "__main__":
    print("[LIVE BITVAVO] starting...")
    notify("🚀 Bot Started", "Bitvavo trading bot is live (real mode)" if not broker.dry_run else "Bitvavo trading bot is running in DRY RUN mode")

    BUY_AMOUNT = float(os.getenv("BUY_AMOUNT", "0.001"))
    SELL_AMOUNT = float(os.getenv("SELL_AMOUNT", "0.001"))
    MARKET = broker.market

    while True:
        try:
            candles = broker.recent_candles(limit=200, interval="1m")
            print("DEBUG candles fetched:", len(candles))
            sig = compute_signal(candles)
            last_close = candles[-1]["close"] if candles else None
            print("signal:", sig, "last close:", last_close)

            notify("📊 Cycle Update", f"Signal: {sig} | Last Close: {last_close}")

            if sig == 1:
                print(f"[TRADE] BUY {BUY_AMOUNT} {MARKET.split('-')[0]}")
                res = broker.buy(BUY_AMOUNT)
                msg = f"✅ BUY {BUY_AMOUNT} {MARKET.split('-')[0]} at {last_close}\nResult: {res}"
                print(msg)
                notify("BUY Order Executed", msg)

            elif sig == -1:
                print(f"[TRADE] SELL {SELL_AMOUNT} {MARKET.split('-')[0]}")
                res = broker.sell(SELL_AMOUNT)
                msg = f"❌ SELL {SELL_AMOUNT} {MARKET.split('-')[0]} at {last_close}\nResult: {res}"
                print(msg)
                notify("SELL Order Executed", msg)

        except Exception as e:
            print("[ERROR]", e)
            notify("⚠️ ERROR", str(e))

        time.sleep(60)  # wait 1 minute per cycle


