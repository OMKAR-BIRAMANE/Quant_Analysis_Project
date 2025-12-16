def compute_rolling_corr(series_a, series_b, window=30):
    df = series_a.to_frame("A").join(series_b.to_frame("B"))
    return df["A"].rolling(window).corr(df["B"])
