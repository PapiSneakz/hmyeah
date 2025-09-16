
Coinbase Advanced Setup (created by assistant)
- Create API Key on Coinbase Developer platform (organizations/{org_id}/apiKeys/{key_id})
- Download EC private key PEM and set COINBASE_API_PRIVATE_KEY_PATH to its path.
- Set COINBASE_API_KEY env var to the API key id.
- Optionally set COINBASE_RETAIL_PORTFOLIO_ID.
- Install dependencies: pip install coinbase-advanced-py python-dotenv pandas numpy
