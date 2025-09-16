"""Example integration module to show how to call the adapter from the existing project.

Put in `integrations/bitvavo/example_run.py` and run to test (it uses dry-run).
"""
import json, logging
from adapter import BitvavoAdapter

logging.basicConfig(level=logging.INFO)

def run_example():
    with open('integrations/bitvavo/config.json') as f:
        conf = json.load(f)
    adapter = BitvavoAdapter(conf)
    logging.info('Dry-run mode: %s', adapter.dry_run)
    bal = adapter.get_balance()
    logging.info('Balance: %s', bal)
    ticker = adapter.get_ticker(conf.get('default_market'))
    logging.info('Ticker: %s', ticker)
    # simulated tiny order
    if isinstance(ticker, dict) and ('price' in ticker or 'last' in ticker):
        price = float(ticker.get('price') or ticker.get('last'))
        amount = round(conf.get('order_size_eur', 10.0) / price, 8)
        resp = adapter.create_order(market=conf.get('default_market'), side='buy', order_type='market', amount=amount)
        logging.info('Order response: %s', resp)
    else:
        logging.warning('Could not parse ticker: %s', ticker)

if __name__ == '__main__':
    run_example()
