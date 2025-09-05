import time
from typing import Dict, Any
from .data import LiveDataSource
from .strategy import get_strategy
from .risk import RiskManager
from .broker import PaperBroker
from .utils import ensure_dir

class PaperTradingLoop:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.ds = LiveDataSource(cfg)
        self.symbol = cfg['market']['symbol']
        self.poll_seconds = int(cfg['paper']['poll_seconds'])
        self.history = int(cfg['paper']['candles_history'])
        self.strat = get_strategy(cfg['strategy']['name'])(cfg['strategy']['params'])
        self.risk = RiskManager(cfg['risk'])
        self.broker = PaperBroker(cfg['paper']['starting_equity'])
        ensure_dir("artifacts")

    def step(self):
        candles = self.ds.get_recent_candles(limit=self.history)
        signal = self.strat.generate_signals(candles).iloc[-1]
        price = float(candles['close'].iloc[-1])

        # 🔍 Debug log for signals
        print(f"[STEP] Last signal={signal}, Price={price:.2f}, Position={self.broker.position}, Equity={self.broker.equity:.2f}")

        if signal == 1 and self.broker.position == 0.0:
            size = self.risk.position_size(self.broker.equity, price)
            sl, tp = self.risk.stops(price)
            self.broker.market("buy", price, size, tp=tp, sl=sl)
            print(f"[TRADE] BUY {self.symbol} @ {price:.2f} size {size}")
        elif signal == -1 and self.broker.position > 0.0:
            self.broker.market("sell", price, self.broker.position)
            print(f"[TRADE] SELL {self.symbol} @ {price:.2f} size ALL")

        # Save state snapshot
        with open("artifacts/paper_state.txt", "w") as f:
            f.write(f"equity={self.broker.equity}\nposition={self.broker.position}\nlast_price={price}\n")

    def run_forever(self):
        print("Starting paper trading loop (Ctrl+C to stop)")
        try:
            while True:
                self.step()
                time.sleep(self.poll_seconds)
        except KeyboardInterrupt:
            print("Stopped.")