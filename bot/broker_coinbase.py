from dataclasses import dataclass
from typing import Any, Dict
import os
from dotenv import load_dotenv
from coinbase.rest import RESTClient

load_dotenv()  # make sure environment variables are loaded


@dataclass
class OrderResult:
    ok: bool
    raw: Any


class CoinbaseBroker:
    def __init__(self, cfg: Dict[str, Any]):
        # Read from .env / config.yaml
        api_key_env = cfg["coinbase"]["api_key_env"]
        api_secret_file_env = cfg["coinbase"]["api_secret_file_env"]

        api_key = os.getenv(api_key_env)
        secret_file = os.getenv(api_secret_file_env)

        if not api_key or not secret_file:
            raise ValueError("Missing API key or secret file. Check .env and config.yaml.")

        with open(secret_file, "r") as f:
            api_secret = f.read()

        self.client = RESTClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=cfg["coinbase"]["base_url"]
        )

        # Market settings
        self.product_id = cfg.get("market", {}).get("symbol", os.getenv("PRODUCT_ID", "BTC-USD"))
        self.timeframe = cfg.get("market", {}).get("timeframe", os.getenv("TIMEFRAME", "1h"))

    def recent_candles(self, limit: int = 300):
        return self.client.get_candles(
            product_id=self.product_id,
            granularity=self.timeframe,
            limit=limit
        )

    def buy(self, quote_usd: float):
        resp = self.client.create_order(
            product_id=self.product_id,
            side="BUY",
            order_configuration={
                "market_market_ioc": {
                    "quote_size": str(quote_usd)
                }
            }
        )
        return OrderResult(ok=True, raw=resp)

    def sell(self, base_size: float):
        resp = self.client.create_order(
            product_id=self.product_id,
            side="SELL",
            order_configuration={
                "market_market_ioc": {
                    "base_size": str(base_size)
                }
            }
        )
        return OrderResult(ok=True, raw=resp)

    def accounts(self):
        return self.client.get_accounts()
