
# Live trading runner for Pepperstone via MT5
from dotenv import load_dotenv
from bot.broker_pepperstone_mt5 import PepperstoneMT5Broker
import os, time, pandas as pd, yaml
from bot.broker_pepperstone_mt5 import PepperstoneMT5Broker

load_dotenv()

with open("config.yaml","r") as f:
    CFG = yaml.safe_load(f)

broker = PepperstoneMT5Broker(CFG)

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
    print("[LIVE MT5] starting...")
    BUY_AMOUNT_USD = float(os.getenv("BUY_AMOUNT_USD","100"))
    SELL_LOTS = float(os.getenv("SELL_LOTS","0.001"))

    while True:
        try:
            candles = broker.recent_candles(limit=200)
            sig = compute_signal(candles)
            last_close = candles[-1]["close"] if candles else None
            print("signal:", sig, "last close:", last_close)
            if sig==1:
                print(f"[TRADE] BUY ${BUY_AMOUNT_USD} -> converting to lots")
                res = broker.buy(usd_amount=BUY_AMOUNT_USD)
                print("result:", res)
            elif sig==-1:
                print(f"[TRADE] SELL {SELL_LOTS} lots")
                res = broker.sell(lots=SELL_LOTS)
                print("result:", res)
        except Exception as e:
            print("[ERROR]", e)
        time.sleep(60)
