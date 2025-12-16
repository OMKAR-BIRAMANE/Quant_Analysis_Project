import pandas as pd

def compute_zscore(series, window=30):
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()

    zscore = (series - mean) / std
    zscore.name = "zscore"
    return zscore
