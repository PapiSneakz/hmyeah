# bot/broker_bitvavo.py
import logging
from integrations.bitvavo.adapter import BitvavoAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class BitvavoBroker:
    def __init__(self, api_key: str, api_secret: str, dry_run: bool = True, default_market: str = "BTC-EUR", order_size_eur: float = 5.0):
        self.adapter = BitvavoAdapter(api_key=api_key, api_secret=api_secret, dry_run=dry_run, default_market=default_market, order_size_eur=order_size_eur)
        self.default_market = default_market
        self.order_size_eur = order_size_eur
        self.dry_run = dry_run
        logging.info(f"BitvavoBroker initialized: market={self.default_market} dry_run={self.dry_run}")

    def recent_candles(self, limit=200, interval="1m"):
        return self.adapter.recent_candles(interval=interval, limit=limit)

    def get_latest_price(self):
        return self.adapter.get_latest_price()

    def get_balance(self):
        return self.adapter.get_balance()

    def get_open_orders(self):
        return self.adapter.get_open_orders()

    def buy(self, amount):
        return self.adapter.create_order(market=self.default_market, side="buy", order_type="market", amount=amount)

    def sell(self, amount):
        return self.adapter.create_order(market=self.default_market, side="sell", order_type="market", amount=amount)

