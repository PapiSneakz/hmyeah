# integrations/bitvavo/adapter.py
import time
import hmac
import hashlib
import json
import requests
import socket


class BitvavoAdapter:
    BASE_URL = "https://api.bitvavo.com/v2"

    def __init__(self, api_key: str, api_secret: str, dry_run: bool = True, default_market: str = "BTC-EUR", order_size_eur: float = 5.0):
        self.apiKey = api_key
        self.apiSecret = api_secret.encode("utf-8")
        self.dry_run = dry_run
        self.default_market = default_market
        self.order_size_eur = order_size_eur
        # session that we force to IPv4 (so Bitvavo sees your whitelisted IPv4)
        self.session = self._get_ipv4_session()

    def _get_ipv4_session(self):
        session = requests.Session()
        original_getaddrinfo = socket.getaddrinfo

        def getaddrinfo_ipv4(host, port, *args, **kwargs):
            return [x for x in original_getaddrinfo(host, port, *args, **kwargs) if x[0] == socket.AF_INET]

        # monkey-patch for current process (keeps it simple)
        socket.getaddrinfo = getaddrinfo_ipv4
        return session

    # --------------------
    # Signing helpers
    # --------------------
    def _headers(self, method: str, endpoint: str, body_str: str = "") -> dict:
        """
        Build the Bitvavo authentication headers. `endpoint` must be the path (e.g. '/balance' or '/order').
        body_str must be the exact JSON string that will be sent (or empty string for GET).
        """
        timestamp = str(int(time.time() * 1000))
        message = timestamp + method.upper() + endpoint + body_str
        signature = hmac.new(self.apiSecret, message.encode("utf-8"), hashlib.sha256).hexdigest()
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
        headers = self._headers("GET", endpoint, "")
        resp = self.session.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def _signed_post(self, endpoint: str, data=None):
        """
        IMPORTANT: we serialize the body once with compact separators, sign that exact string,
        AND send that string as the request body (data=body_str) to avoid signature mismatches.
        """
        url = self.BASE_URL + endpoint
        body_str = json.dumps(data, separators=(",", ":")) if data else ""
        headers = self._headers("POST", endpoint, body_str)
        resp = self.session.post(url, headers=headers, data=body_str, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # --------------------
    # Public endpoints
    # --------------------
    def recent_candles(self, market=None, interval="1m", limit=200):
        market = market or self.default_market
        url = f"{self.BASE_URL}/{market}/candles"
        params = {"interval": interval, "limit": limit}
        resp = self.session.get(url, params=params, timeout=15)
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
                "volume": float(c[5]),
            })
        return candles

    def get_latest_price(self, market=None):
        market = market or self.default_market
        url = f"{self.BASE_URL}/{market}/ticker/price"
        resp = self.session.get(url, timeout=15)
        resp.raise_for_status()
        return float(resp.json()["price"])

    # --------------------
    # Authenticated endpoints
    # --------------------
    def get_balance(self):
        if self.dry_run:
            # return a fake structure similar to live
            return [{"symbol": self.default_market.split("-")[1], "available": "1.00", "inOrder": "0"}]
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
