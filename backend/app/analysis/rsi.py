import pandas as pd


def calculate_rsi(
    data: pd.DataFrame,
    period: int = 14,
):
    """
    Calculate Relative Strength Index (RSI).
    """

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()

    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi