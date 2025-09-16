# integrations/bitvavo/adapter.py
import json
import time
import hmac
import hashlib
import requests

class BitvavoAdapter:
    BASE_URL = "https://api.bitvavo.com/v2"

    def __init__(self, config):
        self.apiKey = config.get("apiKey")
        self.apiSecret = config.get("apiSecret").encode("utf-8")
        self.dry_run = config.get("dry_run", True)
        self.default_market = config.get("default_market", "BTC-EUR")
        self.order_size_eur = config.get("order_size_eur", 5.0)

    def _headers(self, method: str, endpoint: str, body: dict | None = None):
        timestamp = str(int(time.time() * 1000))
        body_str = json.dumps(body) if body else ""
        message = timestamp + method.upper() + endpoint + body_str
        signature = hmac.new(self.apiSecret, message.encode("utf-8"), hashlib.sha256).hexdigest()
        return {
            "Bitvavo-Access-Key": self.apiKey,
            "Bitvavo-Access-Signature": signature,
            "Bitvavo-Access-Timestamp": timestamp,
            "Content-Type": "application/json"
        }

    def _signed_get(self, endpoint: str, params: dict | None = None):
        url = self.BASE_URL + endpoint
        headers = self._headers("GET", endpoint)
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def _signed_post(self, endpoint: str, body: dict | None = None):
        url = self.BASE_URL + endpoint
        headers = self._headers("POST", endpoint, body)
        resp = requests.post(url, headers=headers, data=json.dumps(body or {}))
        resp.raise_for_status()
        return resp.json()

    def recent_candles(self, market=None, interval="1m", limit=200):
        """Fetch recent OHLCV candles; default interval is 1 minute"""
        market = market or self.default_market
        url = f"{self.BASE_URL}/{market}/candles"
        params = {"interval": interval, "limit": limit}

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        candles = []
        for c in data:
            candles.append({
                "time": c[0],
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5])
            })
        return candles

    def get_latest_price(self, market=None):
        """Fetch the exact latest BTC-EUR price (matches Bitvavo UI)"""
        market = market or self.default_market
        url = f"{self.BASE_URL}/{market}/ticker/price"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        return float(data["price"])

    def get_balance(self):
        if self.dry_run:
            return {
                self.default_market.split("-")[0]: {
                    "available": 1.0,
                    "inOrder": 0.0
                }
            }
        return self._signed_get("/balance")

    def get_open_orders(self, market=None):
        market = market or self.default_market
        if self.dry_run:
            return []
        return self._signed_get(f"/{market}/openOrders")

    def create_order(self, market=None, side="buy", order_type="market", amount=0.0):
        market = market or self.default_market
        if self.dry_run:
            print(f"[DRY RUN] {side.upper()} {amount} {market}")
            return {
                "status": "dry_run",
                "side": side,
                "amount": amount,
                "market": market
            }

        endpoint = f"/{market}/orders"
        data = {
            "side": side,
            "type": order_type,
            "amount": str(amount)
        }
        return self._signed_post(endpoint, data)
