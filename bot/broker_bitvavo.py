# bot/broker_bitvavo.py

import logging
from integrations.bitvavo.adapter import BitvavoAdapter


class BitvavoBroker:
    """
    Broker wrapper around BitvavoAdapter.

    Provides higher-level trading operations:
      - Get balances
      - Fetch open orders
      - Place buy/sell orders
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        dry_run: bool = True,
        default_market: str = "BTC-EUR",
        order_size_eur: float = 5.0,
    ):
        self.adapter = BitvavoAdapter(
            api_key=api_key,
            api_secret=api_secret,
            dry_run=dry_run,
            default_market=default_market,
            order_size_eur=order_size_eur,
        )
        self.default_market = default_market
        self.order_size_eur = order_size_eur
        self.dry_run = dry_run

        logging.info(            
        f"Initialized BitvavoBroker (market={default_market}, dry_run={dry_run})"
        )

    # --------------------
    # Account helpers
    # --------------------
    def get_balance(self, symbol: str = "EUR"):
        balances = self.adapter.get_balance()
        if isinstance(balances, list):
            for b in balances:
                if b.get("symbol") == symbol:
                    return float(b.get("available", 0.0))
        elif isinstance(balances, dict):
            return float(balances.get(symbol, {}).get("available", 0.0))
        return 0.0

    def get_open_orders(self, market=None):
        return self.adapter.get_open_orders(market or self.default_market)

    # --------------------
    # Order placement
    # --------------------
    def buy(self, amount_btc: float):
        logging.info(f"Placing BUY order: {amount_btc} BTC {self.default_market}")
        return self.adapter.create_order(
            market=self.default_market, side="buy", order_type="market", amount=amount_btc
        )

    def sell(self, amount_btc: float):
        logging.info(f"Placing SELL order: {amount_btc} BTC {self.default_market}")
        return self.adapter.create_order(
            market=self.default_market,
            side="sell",
            order_type="market",
            amount=amount_btc,
        )

    # --------------------
    # Utility
    # --------------------
    def get_price(self, market=None):
        return self.adapter.get_latest_price(market or self.default_market)
