# integrations/bitvavo/adapter.py
import time
import hmac
import hashlib
import json
import requests

class BitvavoAdapter:
    BASE_URL = "https://api.bitvavo.com/v2"

    def __init__(self, api_key, api_secret, dry_run=True, default_market="BTC-EUR", order_size_eur=5.0):
        self.apiKey = api_key
        self.apiSecret = api_secret.encode("utf-8")
        self.dry_run = dry_run
        self.default_market = default_market
        self.order_size_eur = order_size_eur

    def _headers(self, method: str, endpoint: str, body=None):
        timestamp = str(int(time.time() * 1000))

        body_str = json.dumps(body, separators=(",", ":")) if body else ""
        message = timestamp + method.upper() + endpoint + body_str

        signature = hmac.new(self.apiSecret, message.encode("utf-8"), hashlib.sha256).hexdigest()

        return {
            "Bitvavo-Access-Key": self.apiKey,
            "Bitvavo-Access-Signature": signature,
            "Bitvavo-Access-Timestamp": timestamp,
            "Content-Type": "application/json"
        }

    def _signed_get(self, endpoint, params=None):
        url = self.BASE_URL + endpoint
        headers = self._headers("GET", endpoint)
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def _signed_post(self, endpoint, data=None):
        url = self.BASE_URL + endpoint
        headers = self._headers("POST", endpoint, data)
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()

    # Public endpoints
    def recent_candles(self, market=None, interval="1m", limit=200):
        market = market or self.default_market
        url = f"{self.BASE_URL}/{market}/candles"
        params = {"interval": interval, "limit": limit}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_latest_price(self, market=None):
        market = market or self.default_market
        url = f"{self.BASE_URL}/{market}/ticker/price"
        resp = requests.get(url)
        resp.raise_for_status()
        return float(resp.json()["price"])

    # Authenticated endpoints
    def get_balance(self):
        if self.dry_run:
            return {self.default_market.split("-")[0]: {"available": 1.0, "inOrder": 0.0}}
        return self._signed_get("/balance")

    def get_open_orders(self, market=None):
        market = market or self.default_market
        if self.dry_run:
            return []
        return self._signed_get("/orders", params={"market": market})

    def create_order(self, market=None, side="buy", order_type="market", amount=0.0):
        market = market or self.default_market
        if self.dry_run:
            print(f"[DRY RUN] {side.upper()} {amount} {market}")
            return {"status": "dry_run", "side": side, "amount": amount, "market": market}

        endpoint = "/order"
        data = {
            "market": market,
            "side": side,
            "type": order_type,
            "amount": str(amount)
        }
        return self._signed_post(endpoint, data)
