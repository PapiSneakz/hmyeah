
# AI Trading Bot (Backtest + Paper Trading)

> **Important:** This project is for educational purposes only. It is **not** financial advice. Trading involves substantial risk of loss. Start with **backtesting** and **paper trading**. If you later connect to a live exchange, you are solely responsible for all outcomes, compliance, and taxes.

## Features
- Modular architecture (strategy, risk, broker, data).
- Simple example strategy: SMA crossover with RSI filter.
- Backtesting engine with metrics and an equity curve plot.
- Paper trading using a simulated broker (no real money).
- Optional hooks to use a real exchange via **ccxt** (fill in your own API keys; test responsibility is yours).
- YAML config + `.env` for secrets.

## Quick Start
1. **Python 3.10+** recommended.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in if you plan to use a real exchange via ccxt (optional).
4. Backtest:
   ```bash
   python run_backtest.py
   ```
   A PNG chart and CSV of trades will be written to `artifacts/`.
5. Paper trading (simulated):
   ```bash
   python run_paper_trading.py
   ```
   This will simulate orders using live candles fetched via ccxt **if you configure it**, or from a simple random-walk fallback if no exchange is configured.

## Going Live (At Your Own Risk)
- Implement `CCXTBroker` in `bot/broker.py` with your exchange (e.g., Binance, Kraken, Coinbase) and symbols supported by that exchange.
- Consider exchange-specific constraints (min order size, rate limits, precision).
- Add latency, slippage, and fees modeling in backtests.
- Validate with small amounts you can afford to lose, and understand your jurisdiction's regulations.

## Project Layout
```
ai-trading-bot/
├── README.md
├── requirements.txt
├── config.yaml
├── .env.example
├── run_backtest.py
├── run_paper_trading.py
└── bot/
    ├── __init__.py
    ├── config.py
    ├── data.py
    ├── strategy.py
    ├── risk.py
    ├── broker.py
    ├── backtest.py
    ├── live.py
    └── utils.py
```
