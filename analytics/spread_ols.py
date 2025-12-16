import numpy as np
import pandas as pd
import statsmodels.api as sm

def compute_hedge_ratio(series_a, series_b):
    """
    Computes OLS hedge ratio: A ~ beta * B
    """
    # Align series
    df = pd.concat([series_a, series_b], axis=1).dropna()
    df.columns = ["A", "B"]

    X = sm.add_constant(df["B"])
    y = df["A"]

    model = sm.OLS(y, X).fit()
    beta = model.params["B"]

    return beta

def compute_spread(series_a, series_b, hedge_ratio):
    df = pd.concat([series_a, series_b], axis=1).dropna()
    spread = df.iloc[:, 0] - hedge_ratio * df.iloc[:, 1]
    spread.name = "spread"
    return spread
