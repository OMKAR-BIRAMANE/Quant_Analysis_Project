def check_zscore_alert(zscore_series, threshold):
    """
    Checks if latest z-score breaches threshold
    """
    zscore_series = zscore_series.dropna()
    if zscore_series.empty:
        return None

    latest = zscore_series.iloc[-1]

    if latest >= threshold:
        return f"🔔 Z-Score ABOVE threshold: {latest:.2f}"
    elif latest <= -threshold:
        return f"🔔 Z-Score BELOW threshold: {latest:.2f}"

    return None
