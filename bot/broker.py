from typing import Dict, Any, Optional, List
from dataclasses import dataclass
# import pandas as pd  # reserved for future use

try:
    import ccxt  # type: ignore
except Exception:
    ccxt = None

@dataclass
class Order:
    side: str
    price: float
    size: float
    status: str = "open"
    id: int = 0
    tp: Optional[float] = None
    sl: Optional[float] = None

class PaperBroker:
    def __init__(self, starting_equity: float, fee_pct: float = 0.0005):
        self.equity = starting_equity
        self.position = 0.0
        self.avg_entry = 0.0
        self.fee_pct = fee_pct
        self.order_id = 1
        self.trades: List[Dict[str, Any]] = []

    def _fee(self, price, size):
        return abs(price * size) * self.fee_pct

    def market(self, side: str, price: float, size: float, tp: float=None, sl: float=None) -> Order:
        fee = self._fee(price, size)
        if side == "buy":
            cost = price * size + fee
            if cost > self.equity and price > 0:
                size = max(0.0, (self.equity - fee) / price)
            new_pos = self.position + size
            if new_pos > 0:
                self.avg_entry = (self.avg_entry * self.position + price * size) / new_pos
            self.position = new_pos
            self.equity -= price * size + fee
        else:
            proceeds = price * size - fee
            self.position -= size
            if self.position < 0:
                self.position = 0.0
            self.equity += proceeds

        order = Order(side=side, price=price, size=size, status="filled", id=self.order_id, tp=tp, sl=sl)
        self.order_id += 1
        self.trades.append({
            'id': order.id, 'side': side, 'price': price, 'size': size, 'fee': fee, 'tp': tp, 'sl': sl
        })

        # 🔍 Debug log for PowerShell
        print(f"[ORDER] {side.upper()} {size:.6f} @ {price:.2f} | Fee: {fee:.6f} | New Equity: {self.equity:.2f}")

        return order

class CCXTBroker:
    """Skeleton for a real exchange via ccxt. Fill in safely if you go live."""
    def __init__(self, exchange_name: str, api_key: str, secret: str, password: str = None, sandbox: bool=True):
        if ccxt is None:
            raise RuntimeError("ccxt is not installed.")
        ex_cls = getattr(ccxt, exchange_name, None)
        if ex_cls is None:
            raise ValueError(f"Exchange {exchange_name} not in ccxt")
        self.exchange = ex_cls({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'enableRateLimit': True
        })
        if sandbox and hasattr(self.exchange, 'set_sandbox_mode'):
            self.exchange.set_sandbox_mode(True)

    # Implement create_order, fetch_balance, etc. per your needs and exchange rules.
