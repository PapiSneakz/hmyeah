# bot/live.py
import time
from bot.data import DataFetcher


class TradingLoop:
    def __init__(self, broker, cfg):
        self.broker = broker
        self.cfg = cfg
        self.history = cfg["paper"].get("candles_history", 100)
        self.poll_seconds = cfg["paper"].get("poll_seconds", 60)
        self.symbols = cfg["market"]["symbols"]

        # Use the DataFetcher wrapper that links to the broker's exchange
        self.ds = DataFetcher(broker, cfg)

    def run_forever(self):
        # Test connection first
        try:
            balance = self.broker.fetch_balance()
            print("Connected! Balance summary:", balance)
        except Exception as e:
            print("Authentication failed:", e)
            return

        print(f"Starting live trading loop for symbols: {self.symbols}")

        while True:
            try:
                all_candles = self.ds.get_all_candles(limit=self.history)
                for symbol, candles in all_candles.items():
                    if candles is not None and len(candles) > 0:
                        last_candle = candles.iloc[-1] if hasattr(candles, "iloc") else candles[-1]
                        print(f"[{symbol}] Last candle: {last_candle}")

                        # TODO: implement your SMA/RSI or other strategy logic here
                        # Example:
                        # signal = self.calculate_signal(candles)
                        # self.execute_signal(symbol, signal)
                time.sleep(self.poll_seconds)
            except Exception as e:
                print("[LIVE ERROR]", e)
                time.sleep(5)

    # Optional: add calculate_signal or execute_signal here
