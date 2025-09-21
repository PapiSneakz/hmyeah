# integrations/bitvavo/adapter.py

import time
import hmac
import hashlib
import json
import requests


class BitvavoAdapter:
    """
    Adapter for Bitvavo API.

    Handles authentication, signing, and requests to both public
    and private endpoints. Wraps basic functionality like:
      - Getting balances
      - Fetching candles
      - Placing orders
    """

    BASE_URL = "https://api.bitvavo.com/v2"

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        dry_run: bool = True,
        default_market: str = "BTC-EUR",
        order_size_eur: float = 5.0,
    ):
        self.apiKey = api_key
        self.apiSecret = api_secret.encode("utf-8")
        self.dry_run = dry_run
        self.default_market = default_market
        self.order_size_eur = order_size_eur

    # --------------------
    # Signing helpers
    # --------------------
    def _headers(self, method: str, endpoint: str, body=None) -> dict:
        timestamp = str(int(time.time() * 1000))
        body_str = json.dumps(body, separators=(",", ":")) if body else ""
        message = timestamp + method.upper() + endpoint + body_str
        signature = hmac.new(
            self.apiSecret, message.encode("utf-8"), hashlib.sha256
        ).hexdigest()

                return {
            "Bitvavo-Access-Key": self.apiKey,
            "Bitvavo-Access-Signature": signature,
            "Bitvavo-Access-Timestamp": timestamp,
            "Content-Type": "application/json",
        }

    # --------------------
    # Signed requests
    # --------------------
    def _signed_get(self, endpoint: str, params=None):
        url = self.BASE_URL + endpoint
        headers = self._headers("GET", endpoint)
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def _signed_post(self, endpoint: str, data=None):
        url = self.BASE_URL + endpoint
        headers = self._headers("POST", endpoint, data)
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()

    # --------------------
    # Public endpoints
    # --------------------
    def recent_candles(self, market=None, interval="1m", limit=200):
        market = market or self.default_market
        url = f"{self.BASE_URL}/{market}/candles"
        params = {"interval": interval, "limit": limit}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        candles = []
        for c in data:
            candles.append(
                {
                    "time": c[0],
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "volume": float(c[5]),
                }
