import copy
from bot.config import load_config
from bot.live import PaperTradingLoop


def main():
    cfg = load_config("config.yaml")

    # If "symbols" is provided, loop through them
    symbols = cfg["market"].get("symbols", [])
    if symbols:
        for symbol in symbols:
            cfg_single = copy.deepcopy(cfg)   # ✅ preserve all nested sections
            cfg_single["market"]["symbol"] = symbol
            loop = PaperTradingLoop(cfg_single)
            loop.run_forever()
    else:
        # fallback to single symbol
        loop = PaperTradingLoop(cfg)
        loop.run_forever()


if __name__ == "__main__":
    main()
