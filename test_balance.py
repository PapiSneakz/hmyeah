# test_balance.py
import time, hmac, hashlib, json, requests

API_KEY = "44fafe3d5bd99dfd980b3443f47472b53d4a8ab72a5a85e7b774972217d6eece"
API_SECRET = "bf6b7a875fb2d288a852c578794abc24e1a60a03de8b8d097a7811b9f0dea64776f714eed7aa15eab1366b2d35b42a9c6396612d342a6717e68c970c6e9e1b6a".encode("utf-8")

def sign_get(endpoint):
    ts = str(int(time.time() * 1000))
    message = ts + "GET" + endpoint
    sig = hmac.new(API_SECRET, message.encode("utf-8"), hashlib.sha256).hexdigest()
    return ts, sig

endpoint = "/balance"
ts, sig = sign_get(endpoint)
headers = {
    "Bitvavo-Access-Key": API_KEY,
    "Bitvavo-Access-Signature": sig,
    "Bitvavo-Access-Timestamp": ts,
    "Content-Type": "application/json"
}
resp = requests.get("https://api.bitvavo.com/v2" + endpoint, headers=headers)
print("Status:", resp.status_code)
print("Response:", resp.json())
