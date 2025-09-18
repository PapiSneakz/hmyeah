# run_live_bitvavo.py
import os
import time
import pandas as pd
from bot.broker_bitvavo import BitvavoBroker
from telegram_notifier import TelegramNotifier

# Initialize broker and Telegram notifier
broker = BitvavoBroker()
notifier = TelegramNotifier()

def compute_signal(candles):
    """
    Simple SMA crossover strategy.
    Returns: 1 = buy, -1 = sell, 0 = do nothing
    """
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
    print("[LIVE BITVAVO] Bot started")
    notifier.send("🚀 Bitvavo bot started (live mode)")

    BUY_AMOUNT = float(os.getenv("BUY_AMOUNT", "0.001"))
    SELL_AMOUNT = float(os.getenv("SELL_AMOUNT", "0.001"))
    MARKET = broker.default_market

    while True:
        try:
            # Fetch last 200 candles with 1-minute interval
            candles = broker.recent_candles(limit=200, interval="1m")
            print(f"DEBUG candles fetched: {len(candles)}")
            sig = compute_signal(candles)
            last_close = candles[-1]["close"] if candles else None
            print(f"signal: {sig} last close: {last_close}")

            # Telegram notification every cycle
            notifier.send(f"📊 Signal: {sig} | Last Close: {last_close}")

            # Execute trade if signal
            if sig == 1:
                print(f"[TRADE] BUY {BUY_AMOUNT} {MARKET.split('-')[0]}")
                res = broker.create_order(side="buy", amount=BUY_AMOUNT)
                msg = f"✅ BUY {BUY_AMOUNT} {MARKET.split('-')[0]} at {last_close}\nResult: {res}"
                print(msg)
                notifier.send(msg)

            elif sig == -1:
                print(f"[TRADE] SELL {SELL_AMOUNT} {MARKET.split('-')[0]}")
                res = broker.create_order(side="sell", amount=SELL_AMOUNT)
                msg = f"❌ SELL {SELL_AMOUNT} {MARKET.split('-')[0]} at {last_close}\nResult: {res}"
                print(msg)
                notifier.send(msg)

        except Exception as e:
            print("[ERROR]", e)
            notifier.send(f"⚠️ ERROR: {e}")

        time.sleep(60)  # wait 1 minute per cycle


