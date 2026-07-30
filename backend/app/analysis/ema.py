import pandas as pd


def calculate_ema(
    data: pd.DataFrame,
    period: int = 20,
):
    """
    Calculate Exponential Moving Average (EMA).
    """

    return (
        data["Close"]
        .ewm(
            span=period,
            adjust=False,
        )
        .mean()
    )