# run_live_bitvavo.py
from dotenv import load_dotenv
from bot.broker_bitvavo import BitvavoBroker
import os, time, pandas as pd

load_dotenv()

broker = BitvavoBroker()

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
    BUY_AMOUNT = float(os.getenv("BUY_AMOUNT", "0.001"))
    SELL_AMOUNT = float(os.getenv("SELL_AMOUNT", "0.001"))
    MARKET = broker.market

    while True:
        try:
            # Fetch last 200 candles with 5-minute interval
            candles = broker.recent_candles(limit=200, interval="5m")
            print("DEBUG candles fetched:", len(candles))
            sig = compute_signal(candles)
            last_close = candles[-1]["close"] if candles else None
            print("signal:", sig, "last close:", last_close)

            if sig == 1:
                print(f"[TRADE] BUY {BUY_AMOUNT} {MARKET.split('-')[0]}")
                res = broker.buy(BUY_AMOUNT)
                print("result:", res)

            elif sig == -1:
                print(f"[TRADE] SELL {SELL_AMOUNT} {MARKET.split('-')[0]}")
                res = broker.sell(SELL_AMOUNT)
                print("result:", res)

        except Exception as e:
            print("[ERROR]", e)

        time.sleep(60)
