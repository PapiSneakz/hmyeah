# bot/broker_bitvavo.py
import os
import json
from integrations.bitvavo.adapter import BitvavoAdapter

class BitvavoBroker:
    def __init__(self, config_path="integrations/bitvavo/config.json"):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Bitvavo config not found: {config_path}")
        with open(config_path, "r") as f:
            cfg = json.load(f)

        self.market = cfg.get("market", "BTC-EUR")
        self.adapter = BitvavoAdapter(cfg)

    def account_info(self):
        return self.adapter.get_balance()

    def positions_get(self):
        return self.adapter.get_open_orders(market=self.market)

    def buy(self, amount):
        return self.adapter.create_order(
            market=self.market,
            side="buy",
            order_type="market",
            amount=amount
        )

    def sell(self, amount):
        return self.adapter.create_order(
            market=self.market,
            side="sell",
            order_type="market",
            amount=amount
        )

    def recent_candles(self, limit=200, interval="5m"):
        """
        Fetch recent candles from Bitvavo.
        interval: 5m, 15m, 1h, etc.
        """
        candles = self.adapter.recent_candles(market=self.market, interval=interval, limit=limit)
        if not candles:
            raise ValueError("No candles returned from Bitvavo API")
        return candles
