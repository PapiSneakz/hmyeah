import time
from typing import Dict, Any
from .data import LiveDataSource
from .strategy import get_strategy
from .risk import RiskManager
from .broker import PaperBroker, CCXTBroker
from .utils import ensure_dir


class TradingLoop:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.ds = LiveDataSource(cfg)
        self.symbol = cfg['market']['symbol']
        self.poll_seconds = int(cfg['market'].get('poll_seconds', 60))
        self.history = int(cfg['market'].get('candles_history', 200))
        self.strat = get_strategy(cfg['strategy']['name'])(cfg['strategy']['params'])
        self.risk = RiskManager(cfg['risk'])

        # ✅ Choose broker based on mode
        if cfg['exchange'].get('mode', 'paper') == "paper":
            self.broker = PaperBroker(cfg['paper']['starting_equity'])
            print("[INIT] Using PaperBroker (simulation mode)")
        else:
            self.broker = CCXTBroker(
                exchange_name=cfg['exchange']['name'],
                api_key=cfg['exchange'].get('api_key'),
                secret=cfg['exchange'].get('secret'),
                password=cfg['exchange'].get('password'),
                sandbox=cfg['exchange'].get('sandbox', False)
            )
            print(f"[INIT] Using CCXTBroker (LIVE mode) on {cfg['exchange']['name']}")

        ensure_dir("artifacts")

    def step(self):
        candles = self.ds.get_recent_candles(limit=self.history)
        signal = self.strat.generate_signals(candles).iloc[-1]
        price = float(candles['close'].iloc[-1])

        # Debug log
        print(f"[STEP] Last signal={signal}, Price={price:.2f}")

        if signal == 1:
            size = self.risk.position_size(1000, price)  # ⚠️ For PaperBroker: equity. For CCXT, better to query balance.
            if isinstance(self.broker, PaperBroker):
                sl, tp = self.risk.stops(price)
                self.broker.market("buy", price, size, tp=tp, sl=sl)
            else:
                self.broker.market(self.symbol, "buy", size)
            print(f"[TRADE] BUY {self.symbol} @ {price:.2f} size {size}")

        elif signal == -1:
            if isinstance(self.broker, PaperBroker):
                if self.broker.position > 0.0:
                    self.broker.market("sell", price, self.broker.position)
                    print(f"[TRADE] SELL {self.symbol} @ {price:.2f} size ALL")
            else:
                # For live mode: simple example (no position tracking here)
                self.broker.market(self.symbol, "sell", size=0.001)  # ⚠️ replace with your desired size
                print(f"[TRADE] LIVE SELL {self.symbol} @ {price:.2f}")

        # Save snapshot for paper mode
        if isinstance(self.broker, PaperBroker):
            with open("artifacts/paper_state.txt", "w") as f:
                f.write(f"equity={self.broker.equity}\nposition={self.broker.position}\nlast_price={price}\n")

    def run_forever(self):
        mode = self.cfg['exchange'].get('mode', 'paper')
        print(f"Starting trading loop in {mode.upper()} mode (Ctrl+C to stop)")
        try:
            while True:
                self.step()
                time.sleep(self.poll_seconds)
        except KeyboardInterrupt:
            print("Stopped.")
