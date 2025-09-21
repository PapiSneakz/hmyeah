# bot/test_order.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.bitvavo.adapter import BitvavoAdapter

# --- Put your new key/secret here (or load from env) ---
API_KEY = "44fafe3d5bd99dfd980b3443f47472b53d4a8ab72a5a85e7b774972217d6eece"
API_SECRET = "bf6b7a875fb2d288a852c578794abc24e1a60a03de8b8d097a7811b9f0dea64776f714eed7aa15eab1366b2d35b42a9c6396612d342a6717e68c970c6e9e1b6a"

adapter = BitvavoAdapter(api_key=API_KEY, api_secret=API_SECRET, dry_run=False, default_market="BTC-EUR")

print("Placing LIVE test order (buy 0.0001 BTC)...")
try:
    resp = adapter.create_order(market="BTC-EUR", side="buy", order_type="market", amount=0.0001)
    print("✅ Order placed:", resp)
except Exception as e:
    print("❌ Error:", e)
