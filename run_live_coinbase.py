# Live trading runner (Option B, 2025 Coinbase API)
from dotenv import load_dotenv
import os, time, pandas as pd, yaml
from bot.broker_coinbase import CoinbaseBroker

load_dotenv()

# Load config.yaml
with open("config.yaml", "r") as f:
    CFG = yaml.safe_load(f)

# Initialize Coinbase broker
broker = CoinbaseBroker(CFG)

# --- Strategy ---
def compute_signal(candles):
    df = pd.DataFrame(candles)
    if len(df) < 50:
        return 0
    df["sma_fast"] = df["close"].rolling(10).mean()
    df["sma_slow"] = df["close"].rolling(40).mean()
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if prev["sma_fast"] <= prev["sma_slow"] and last["sma_fast"] > last["sma_slow"]:
        return 1   # bullish crossover → buy
    if prev["sma_fast"] >= prev["sma_slow"] and last["sma_fast"] < last["sma_slow"]:
        return -1  # bearish crossover → sell
    return 0

# --- Runner ---
if __name__ == "__main__":
    print("[LIVE] starting...")
    BUY_AMOUNT_USD = float(os.getenv("BUY_AMOUNT_USD", "100"))     # $100 per buy
    SELL_AMOUNT_BASE = float(os.getenv("SELL_AMOUNT_BASE", "0.001"))  # 0.001 BTC per sell

    while True:
        try:
            candles = broker.recent_candles(limit=200)
            sig = compute_signal(candles)

            last_close = candles[-1]["close"] if candles else None
            print("signal:", sig, "last close:", last_close)

            if sig == 1:
                print(f"[TRADE] BUY {BUY_AMOUNT_USD} USD of {broker.product_id}")
                result = broker.buy(BUY_AMOUNT_USD)
                print("Order result:", result)

            elif sig == -1:
                print(f"[TRADE] SELL {SELL_AMOUNT_BASE} {broker.product_id.split('-')[0]}")
                result = broker.sell(SELL_AMOUNT_BASE)
                print("Order result:", result)

        except Exception as e:
            print("[ERROR]", e)

        time.sleep(60)
