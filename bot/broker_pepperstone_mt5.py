from dataclasses import dataclass
from typing import Any, Dict, Optional
import os, time, logging
from dotenv import load_dotenv
load_dotenv()
try:
    import MetaTrader5 as mt5
except Exception as e:
    mt5 = None

logger = logging.getLogger(__name__)

@dataclass
class OrderResult:
    ok: bool
    raw: Any

class PepperstoneMT5Broker:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg.get("pepperstone_mt5", cfg)
        self.login = int(os.getenv("MT5_LOGIN", str(self.cfg.get("login","0")) or "0"))
        self.password = os.getenv("MT5_PASSWORD", self.cfg.get("password",""))
        self.server = os.getenv("MT5_SERVER", self.cfg.get("server",""))
        self.terminal_path = os.getenv("MT5_TERMINAL_PATH", self.cfg.get("terminal_path", None))
        self.symbol = self.cfg.get("symbol", "BTCUSD")
        self.default_lot = float(self.cfg.get("lot", 0.01))
        if mt5 is None:
            raise RuntimeError("MetaTrader5 module not installed. pip install MetaTrader5")
        self._init_mt5()

    def _init_mt5(self):
        if self.terminal_path:
            ok = mt5.initialize(self.terminal_path)
        else:
            ok = mt5.initialize()
        if not ok:
            mt5.initialize()
        if self.login:
            try:
                mt5.login(self.login, password=self.password, server=self.server)
            except Exception:
                # some MT5 setups don't require explicit login from python if terminal already logged in
                pass

    def recent_candles(self, limit:int=200, timeframe=mt5.TIMEFRAME_M60):
        # returns list of dicts with open/high/low/close/time
        from datetime import datetime, timedelta
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, limit)
        res=[]
        for r in rates:
            res.append({"time": r[0], "open": r[1], "high": r[2], "low": r[3], "close": r[4], "tick_volume": r[5]})
        return res

    def get_price(self):
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick:
            raise RuntimeError("No tick for symbol "+self.symbol)
        return {"bid": tick.bid, "ask": tick.ask, "last": (tick.bid+tick.ask)/2}

    def get_balance(self):
        info = mt5.account_info()
        if info is None:
            return None
        return {"balance": info.balance, "equity": info.equity, "margin_free": info.margin_free}

    def usd_to_lots(self, usd_amount:float):
        # APPROXIMATION: assume 1 lot == 1 base unit (e.g., 1 BTC)
        price = self.get_price()["ask"]
        lots = usd_amount / price
        # enforce minimal lot step
        sym = mt5.symbol_info(self.symbol)
        lot_min = sym.volume_min if sym else 0.01
        lot_step = sym.volume_step if sym else 0.01
        # round down to nearest step
        import math
        lots = max(lot_min, math.floor(lots/lot_step)*lot_step)
        return round(lots, 8)

    def buy(self, usd_amount:Optional[float]=None, lots:Optional[float]=None):
        if lots is None:
            if usd_amount is None:
                lots = self.default_lot
            else:
                lots = self.usd_to_lots(usd_amount)
        price = mt5.symbol_info_tick(self.symbol).ask
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(lots),
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "deviation": 100,
            "magic": 123456,
            "comment": "pepperstone_bot_buy",
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        res = mt5.order_send(request)
        ok = res is not None and getattr(res, "retcode", None) == mt5.TRADE_RETCODE_DONE
        return OrderResult(ok=ok, raw=res)

    def sell(self, lots:Optional[float]=None):
        # sell by lots
        if lots is None:
            lots = self.default_lot
        price = mt5.symbol_info_tick(self.symbol).bid
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(lots),
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": 100,
            "magic": 123456,
            "comment": "pepperstone_bot_sell",
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        res = mt5.order_send(request)
        ok = res is not None and getattr(res, "retcode", None) == mt5.TRADE_RETCODE_DONE
        return OrderResult(ok=ok, raw=res)

    def positions(self):
        return mt5.positions_get()

    def close_all(self):
        positions = mt5.positions_get()
        if not positions:
            return
        for p in positions:
            vol = p.volume
            sym = p.symbol
            if p.type==0:
                # long -> sell
                mt5.order_send({"action": mt5.TRADE_ACTION_DEAL, "symbol": sym, "volume": vol, "type": mt5.ORDER_TYPE_SELL, "price": mt5.symbol_info_tick(sym).bid, "deviation":100, "type_filling": mt5.ORDER_FILLING_FOK})
            else:
                mt5.order_send({"action": mt5.TRADE_ACTION_DEAL, "symbol": sym, "volume": vol, "type": mt5.ORDER_TYPE_BUY, "price": mt5.symbol_info_tick(sym).ask, "deviation":100, "type_filling": mt5.ORDER_FILLING_FOK})
            time.sleep(0.2)
