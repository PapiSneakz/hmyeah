
from bot.config import load_config
from bot.backtest import Backtester
from bot.strategy import get_strategy
from bot.risk import RiskManager
from bot.data import HistoricalDataSource
from bot.utils import ensure_dir

def main():
    cfg = load_config("config.yaml")
    ensure_dir("artifacts")
    data = HistoricalDataSource(cfg)
    candles = data.get_historical(limit=2000)  # DataFrame with ['timestamp','open','high','low','close','volume']
    StrategyCls = get_strategy(cfg['strategy']['name'])
    strat = StrategyCls(cfg['strategy']['params'])
    risk = RiskManager(cfg['risk'])
    bt = Backtester(cfg['backtest'], strat, risk)
    results = bt.run(candles)
    print("Backtest Metrics:", results['metrics'])
    print("Wrote artifacts to ./artifacts")

if __name__ == "__main__":
    main()
