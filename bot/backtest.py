
from typing import Dict, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .risk import RiskManager
from .strategy import BaseStrategy
from .broker import PaperBroker
from .utils import ensure_dir

class Backtester:
    def __init__(self, params: Dict[str, Any], strategy: BaseStrategy, risk: RiskManager):
        self.params = params
        self.strategy = strategy
        self.risk = risk
        self.fee_pct = float(params.get('fee_pct', 0.0005))
        self.slippage_pct = float(params.get('slippage_pct', 0.0002))

    def run(self, candles: pd.DataFrame):
        df = candles.copy().reset_index(drop=True)
        signals = self.strategy.generate_signals(df)
        equity = self.params.get('starting_equity', 10000.0)
        broker = PaperBroker(starting_equity=equity, fee_pct=self.fee_pct)

        position = 0.0
        trades = []
        equity_curve = []

        for i in range(len(df)):
            price = float(df.loc[i, 'close'])
            signal = int(signals.iloc[i])
            # Apply simple slippage
            price_exec = price * (1 + (self.slippage_pct if signal != 0 else 0))

            if signal == 1 and position == 0.0:
                size = self.risk.position_size(broker.equity, price_exec)
                sl, tp = self.risk.stops(price_exec)
                broker.market("buy", price_exec, size, tp=tp, sl=sl)
                position += size
                trades.append({'ts': df.loc[i,'timestamp'], 'side':'buy', 'price': price_exec, 'size': size})
            elif signal == -1 and position > 0.0:
                broker.market("sell", price_exec, position)
                trades.append({'ts': df.loc[i,'timestamp'], 'side':'sell', 'price': price_exec, 'size': position})
                position = 0.0

            # Track equity as cash + position value
            mark_value = broker.equity + position * price
            equity_curve.append(mark_value)

        # Metrics
        ec = np.array(equity_curve)
        returns = np.diff(ec) / ec[:-1] if len(ec) > 1 else np.array([])
        total_return = (ec[-1] / ec[0]) - 1 if len(ec) > 1 else 0.0
        sharpe = (returns.mean() / (returns.std() + 1e-12)) * np.sqrt(252*24*60) if len(returns) > 2 else 0.0
        max_dd = 0.0
        peak = -1e18
        for v in ec:
            if v > peak: peak = v
            dd = (peak - v)/peak if peak > 0 else 0.0
            if dd > max_dd: max_dd = dd

        # Save artifacts
        ensure_dir("artifacts")
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv("artifacts/backtest_trades.csv", index=False)

        plt.figure()
        plt.plot(ec)
        plt.title("Equity Curve")
        plt.xlabel("Step")
        plt.ylabel("Equity")
        plt.savefig("artifacts/equity_curve.png", dpi=160, bbox_inches='tight')
        plt.close()

        return {
            'metrics': {
                'final_equity': float(ec[-1]) if len(ec) else equity,
                'total_return_pct': float(total_return*100),
                'sharpe_like': float(sharpe),
                'max_drawdown_pct': float(max_dd*100),
                'num_trades': int(len(trades_df))
            },
            'files': {
                'trades_csv': "artifacts/backtest_trades.csv",
                'equity_curve_png': "artifacts/equity_curve.png"
            }
        }
