from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.trade_models import PaperTrade


class PortfolioService:

    @staticmethod
    def get_portfolio_summary(db: Session):

        INITIAL_CAPITAL = 70000

        total_trades = (
            db.query(PaperTrade).count()
        )

        open_trades = (
            db.query(PaperTrade)
            .filter(PaperTrade.status == "OPEN")
            .count()
        )

        closed_trades = (
            db.query(PaperTrade)
            .filter(PaperTrade.status == "CLOSED")
            .count()
        )

        # -------------------------
        # REALIZED P&L
        # -------------------------

        realized_pnl = (
            db.query(func.sum(PaperTrade.pnl))
            .filter(PaperTrade.status == "CLOSED")
            .scalar()
            or 0
        )

        # -------------------------
        # WIN / LOSS
        # -------------------------

        winning_trades = (
            db.query(PaperTrade)
            .filter(
                PaperTrade.status == "CLOSED",
                PaperTrade.pnl > 0,
            )
            .count()
        )

        losing_trades = (
            db.query(PaperTrade)
            .filter(
                PaperTrade.status == "CLOSED",
                PaperTrade.pnl < 0,
            )
            .count()
        )

        # -------------------------
        # PROFIT / LOSS
        # -------------------------

        total_profit = (
            db.query(func.sum(PaperTrade.pnl))
            .filter(
                PaperTrade.status == "CLOSED",
                PaperTrade.pnl > 0,
            )
            .scalar()
            or 0
        )

        total_loss = (
            db.query(func.sum(PaperTrade.pnl))
            .filter(
                PaperTrade.status == "CLOSED",
                PaperTrade.pnl < 0,
            )
            .scalar()
            or 0
        )

        # -------------------------
        # EXTREMES
        # -------------------------

        largest_win = (
            db.query(func.max(PaperTrade.pnl))
            .filter(
                PaperTrade.status == "CLOSED"
            )
            .scalar()
            or 0
        )

        largest_loss = (
            db.query(func.min(PaperTrade.pnl))
            .filter(
                PaperTrade.status == "CLOSED"
            )
            .scalar()
            or 0
        )

        # -------------------------
        # AVERAGES
        # -------------------------

        average_win = (
            db.query(func.avg(PaperTrade.pnl))
            .filter(
                PaperTrade.status == "CLOSED",
                PaperTrade.pnl > 0,
            )
            .scalar()
            or 0
        )

        average_loss = (
            db.query(func.avg(PaperTrade.pnl))
            .filter(
                PaperTrade.status == "CLOSED",
                PaperTrade.pnl < 0,
            )
            .scalar()
            or 0
        )

        # -------------------------
        # WIN RATE
        # -------------------------

        if closed_trades > 0:
            win_rate = (
                winning_trades
                / closed_trades
            ) * 100
        else:
            win_rate = 0

        # -------------------------
        # BALANCE
        # -------------------------

        current_balance = (
            INITIAL_CAPITAL
            + realized_pnl
        )
        return_percentage = (
            realized_pnl / INITIAL_CAPITAL
        ) * 100

        return {
            "capital": INITIAL_CAPITAL,

            "current_balance": round(
                current_balance, 2
            ),

            "realized_pnl": round(
                realized_pnl, 2
            ),
            "net_pnl": round(
                realized_pnl, 2
            ),
            "return_percentage": round(
                return_percentage, 2
            ),

            "total_trades": total_trades,

            "open_trades": open_trades,

            "closed_trades": closed_trades,

            "winning_trades": winning_trades,

            "losing_trades": losing_trades,

            "win_rate": round(
                win_rate, 2
            ),

            "total_profit": round(
                total_profit, 2
            ),

            "total_loss": round(
                total_loss, 2
            ),

            "largest_win": round(
                largest_win, 2
            ),

            "largest_loss": round(
                largest_loss, 2
            ),

            "average_win": round(
                average_win, 2
            ),

            "average_loss": round(
                average_loss, 2
            ),
        }