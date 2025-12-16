import pandas as pd

def resample_ticks(df, timeframe="1s"):
    """
    timeframe: '1s', '1m' (1 min), '5m'
    """
    bars = {}

    for symbol in df["symbol"].unique():
        symbol_df = df[df["symbol"] == symbol].copy()
        symbol_df.set_index("timestamp", inplace=True)

        ohlc = symbol_df["price"].resample(timeframe).ohlc()
        volume = symbol_df["qty"].resample(timeframe).sum()

        bars[symbol] = pd.concat([ohlc, volume], axis=1)
        bars[symbol].columns = ["open", "high", "low", "close", "volume"]
        bars[symbol].dropna(inplace=True)

    return bars
