# run_paper_trading.py
import yaml
from bot.broker_pepperstone_mt5 import PepperstoneMT5Broker
from bot.live import TradingLoop
from bot.broker import Broker
from bot.broker_pepperstone_mt5 import PepperstoneMT5Broker

 # assuming you have a Broker class


def main():
    # Load config
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    # Initialize broker
    broker = Broker(cfg)

    # Start trading loop
    loop = TradingLoop(broker, cfg)
    loop.run_forever()


if __name__ == "__main__":
    main()
