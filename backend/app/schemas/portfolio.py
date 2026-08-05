from pydantic import BaseModel


class PortfolioResponse(BaseModel):
    capital: float

    current_balance: float

    net_pnl: float

    total_trades: int

    open_trades: int

    closed_trades: int

    winning_trades: int

    losing_trades: int

    win_rate: float

    total_profit: float

    total_loss: float

    largest_win: float

    largest_loss: float

    average_win: float

    average_loss: float