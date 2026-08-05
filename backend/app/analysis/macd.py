import pandas as pd


def calculate_macd(data: pd.DataFrame):
    """
    Calculate MACD.
    """

    ema12 = data["Close"].ewm(
        span=12,
        adjust=False,
    ).mean()

    ema26 = data["Close"].ewm(
        span=26,
        adjust=False,
    ).mean()

    macd = ema12 - ema26

    signal = macd.ewm(
        span=9,
        adjust=False,
    ).mean()

    histogram = macd - signal

    return macd, signal, histogram