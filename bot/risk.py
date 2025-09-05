
from typing import Dict, Any
import math

class RiskManager:
    def __init__(self, params: Dict[str, Any]):
        self.max_position_pct = float(params.get('max_position_pct', 0.2))
        self.stop_loss_pct = float(params.get('stop_loss_pct', 0.02))
        self.take_profit_pct = float(params.get('take_profit_pct', 0.04))

    def position_size(self, equity: float, price: float) -> float:
        dollar_risk = equity * self.max_position_pct
        size = dollar_risk / price
        return math.floor(size * 1e6) / 1e6  # truncate to 6 dp for safety

    def stops(self, entry_price: float):
        sl = entry_price * (1 - self.stop_loss_pct)
        tp = entry_price * (1 + self.take_profit_pct)
        return sl, tp
