import time
from typing import Dict, Any
import pandas as pd
import numpy as np

try:
    import ccxt  # type: ignore
except Exception:
    ccxt = None


class HistoricalDataSource:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.symbol = cfg['market']['symbol']
        self.timeframe = cfg['market']['timeframe']
        self.exchange_name = cfg['exchange']['name']
        self.rate_limit_ms = cfg['exchange'].get('rate_limit_ms', 250)

        if self.exchange_name and ccxt:
            ex_cls = getattr(ccxt, self.exchange_name, None)
            if ex_cls is None:
                raise ValueError(f"Exchange {self.exchange_name} not in ccxt")
            self.exchange = ex_cls({'enableRateLimit': True})
        else:
            self.exchange = None

    def get_historical(self, limit: int = 2000) -> pd.DataFrame:
        if self.exchange:
            print(f"[DATA] Fetching {limit} candles for {self.symbol} ({self.timeframe}) from {self.exchange_name}")
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=limit)
            return pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])

        # Fallback: synthetic candles for offline mode
        ts = int(time.time()*1000)
        step_ms = {'1m': 60_000, '5m': 300_000, '15m': 900_000, '1h': 3_600_000}.get(self.timeframe, 60_000)
        prices = [20000.0]
        for _ in range(limit-1):
            prices.append(prices[-1] * (1 + np.random.normal(0, 0.001)))

        open_ = np.array(prices[:-1])
        close = np.array(prices[1:])
        high = np.maximum(open_, close) * (1 + np.random.rand(len(open_))*0.002)
        low = np.minimum(open_, close) * (1 - np.random.rand(len(open_))*0.002)
        volume = np.random.rand(len(open_))*10
        timestamps = [ts - step_ms*(len(open_)-i) for i in range(len(open_))]

        return pd.DataFrame({
            'timestamp': timestamps,
            'open': open_,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })


class LiveDataSource:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.symbol = cfg['market']['symbol']
        self.timeframe = cfg['market']['timeframe']
        self.exchange_name = cfg['exchange']['name']

        if self.exchange_name and ccxt:
            ex_cls = getattr(ccxt, self.exchange_name, None)
            if ex_cls is None:
                raise ValueError(f"Exchange {self.exchange_name} not in ccxt")

            # ✅ Load API keys if provided in config
            self.exchange = ex_cls({
                'apiKey': cfg['exchange'].get('api_key'),
                'secret': cfg['exchange'].get('secret'),
                'password': cfg['exchange'].get('password'),
                'enableRateLimit': True
            })
        else:
            self.exchange = None

    def get_recent_candles(self, limit: int = 200) -> pd.DataFrame:
        if self.exchange:
            print(f"[DATA] Fetching {limit} live candles for {self.symbol} ({self.timeframe}) from {self.exchange_name}")
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=limit)
            return pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])

        # Fallback: synthetic if no exchange
        return HistoricalDataSource(self.cfg).get_historical(limit=limit)
