from typing import Dict, Any
import pandas as pd
import ta

class BaseStrategy:
    def __init__(self, params: Dict[str, Any]):
        self.params = params

    def generate_signals(self, candles: pd.DataFrame) -> pd.Series:
        raise NotImplementedError


class SMARSI(BaseStrategy):
    def generate_signals(self, candles: pd.DataFrame) -> pd.Series:
        # ⚡ More active defaults
        fast = self.params.get('fast_sma', 10)      # was 20
        slow = self.params.get('slow_sma', 30)      # was 50
        rsi_p = self.params.get('rsi_period', 14)
        rsi_buy_below = self.params.get('rsi_buy_below', 45)   # was 35
        rsi_sell_above = self.params.get('rsi_sell_above', 55) # was 65

        df = candles.copy()
        df['sma_fast'] = df['close'].rolling(fast).mean()
        df['sma_slow'] = df['close'].rolling(slow).mean()
        df['rsi'] = ta.momentum.rsi(df['close'], window=rsi_p)

        signal = pd.Series(0, index=df.index)

        cross_up = (df['sma_fast'] > df['sma_slow']) & (df['sma_fast'].shift(1) <= df['sma_slow'].shift(1))
        cross_down = (df['sma_fast'] < df['sma_slow']) & (df['sma_fast'].shift(1) >= df['sma_slow'].shift(1))

        # ✅ Looser logic: if RSI OR SMA crossover is enough, fire a trade
        signal[(cross_up) | (df['rsi'] < rsi_buy_below)] = 1
        signal[(cross_down) | (df['rsi'] > rsi_sell_above)] = -1

        # Optional debug print
        if not signal[signal != 0].empty:
            last_idx = signal[signal != 0].index[-1]
            print(f"SMARSI signal: {signal[last_idx]} at price {df['close'].iloc[-1]} (RSI={df['rsi'].iloc[-1]:.2f})")

        return signal.fillna(0)


class ScalpingStrategy(BaseStrategy):
    def generate_signals(self, candles: pd.DataFrame) -> pd.Series:
        ema_fast = self.params.get('ema_fast', 5)
        ema_slow = self.params.get('ema_slow', 20)
        rsi_p = self.params.get('rsi_period', 14)
        rsi_overbought = self.params.get('rsi_overbought', 70)
        rsi_oversold = self.params.get('rsi_oversold', 30)
        vol_window = self.params.get('volume_ma', 10)

        df = candles.copy()
        df['ema_fast'] = df['close'].ewm(span=ema_fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=ema_slow, adjust=False).mean()
        df['rsi'] = ta.momentum.rsi(df['close'], window=rsi_p)
        df['vol_ma'] = df['volume'].rolling(vol_window).mean()

        signal = pd.Series(0, index=df.index)

        long_entry = (df['ema_fast'] > df['ema_slow']) & (df['rsi'] > rsi_oversold) & (df['volume'] > df['vol_ma'])
        short_entry = (df['ema_fast'] < df['ema_slow']) & (df['rsi'] < rsi_overbought) & (df['volume'] > df['vol_ma'])

        signal[long_entry] = 1
        signal[short_entry] = -1

        if not signal[signal != 0].empty:
            last_idx = signal[signal != 0].index[-1]
            print(f"Scalping signal: {signal[last_idx]} at price {df['close'].iloc[-1]} (RSI={df['rsi'].iloc[-1]:.2f})")

        return signal.fillna(0)


def get_strategy(name: str):
    if name == "sma_rsi":
        return SMARSI
    elif name == "scalping":
        return ScalpingStrategy
    raise ValueError(f"Unknown strategy: {name}")
