"""
Coinbase Advanced Trade wrapper for this bot.
Uses the official SDK: coinbase-advanced-py
Auth: API Key ID + EC private key PEM.
No passphrase, no secret string.
"""
from __future__ import annotations
import os, uuid
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone

from coinbase.rest import RESTClient

GRANULARITY_MAP = {
    "1m": "ONE_MINUTE",
    "3m": "THREE_MINUTE",
    "5m": "FIVE_MINUTE",
    "15m": "FIFTEEN_MINUTE",
    "30m": "THIRTY_MINUTE",
    "1h": "ONE_HOUR",
    "2h": "TWO_HOUR",
    "4h": "FOUR_HOUR",
    "6h": "SIX_HOUR",
    "1d": "ONE_DAY",
}

@dataclass
class CoinbaseConfig:
    api_key: str = ""  # not used for Advanced Trade
    api_private_key_path: str = ""
    product_id: str = "BTC-USD"
    timeframe: str = "1h"
    retail_portfolio_id: Optional[str] = None
    base_url: str = "api.coinbase.com"

class CoinbaseAdvanced:
    def __init__(self, cfg: CoinbaseConfig):
        if cfg.timeframe not in GRANULARITY_MAP:
            raise ValueError(f"Unsupported timeframe: {cfg.timeframe}")
        self.cfg = cfg
        if not os.path.exists(cfg.api_private_key_path):
            raise FileNotFoundError(f"Private key PEM not found: {cfg.api_private_key_path}")
        
        # FIX: Only use key_file for Advanced Trade, do not pass api_key
        self.client = RESTClient(
            key_file=cfg.api_private_key_path,
            base_url=cfg.base_url,
        )

    def get_candles(self, limit: int = 300) -> List[Dict[str, Any]]:
        gran = GRANULARITY_MAP[self.cfg.timeframe]
        bucket_seconds = self._bucket_seconds(self.cfg.timeframe)
        end = datetime.now(timezone.utc)
        start = end - timedelta(seconds=bucket_seconds * limit)
        resp = self.client.get_candles(
            product_id=self.cfg.product_id,
            start=start.isoformat(),
            end=end.isoformat(),
            granularity=gran,
            limit=limit,
        )
        candles = []
        for c in getattr(resp, "candles", []):
            candles.append({
                "start": c.start,
                "end": c.end,
                "low": float(c.low),
                "high": float(c.high),
                "open": float(c.open),
                "close": float(c.close),
                "volume": float(c.volume),
            })
        candles.sort(key=lambda x: x["start"])
        return candles

    def _bucket_seconds(self, tf: str) -> int:
        return {
            "1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800,
            "1h": 3600, "2h": 7200, "4h": 14400, "6h": 21600, "1d": 86400
        }[tf]

    def list_accounts(self) -> Any:
        return self.client.get_accounts()

    def market_buy_quote(self, quote_size: str) -> Any:
        return self.client.market_order_buy(
            client_order_id=str(uuid.uuid4()),
            product_id=self.cfg.product_id,
            quote_size=str(quote_size),
            retail_portfolio_id=self.cfg.retail_portfolio_id,
        )

    def market_sell_base(self, base_size: str) -> Any:
        return self.client.market_order_sell(
            client_order_id=str(uuid.uuid4()),
            product_id=self.cfg.product_id,
            base_size=str(base_size),
            retail_portfolio_id=self.cfg.retail_portfolio_id,
        )
