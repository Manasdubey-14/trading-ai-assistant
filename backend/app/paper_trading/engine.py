from datetime import datetime
from app.database.position_model import Position

from sqlalchemy.orm import Session

from app.database.trade_models import PaperTrade
from app.services.pnl_service import PnLService


class PaperTradingEngine:

    @staticmethod
    def create_trade(
        db: Session,
        trade,
    ):

        db_trade = PaperTrade(
            symbol=trade.symbol,
            trade_type=trade.trade_type.upper(),
            quantity=trade.quantity,
            entry_price=trade.entry_price,
            stop_loss=trade.stop_loss,
            target=trade.target,
            strategy=getattr(trade, "strategy", None),
            timeframe=getattr(trade, "timeframe", None),
            confidence=getattr(trade, "confidence", None),
            notes=getattr(trade, "notes", None),
            pnl=0,
            status="OPEN",
        )

        db.add(db_trade)
        db.commit()
        db.refresh(db_trade)

        db_position = Position(
            symbol=db_trade.symbol,
            side=db_trade.trade_type,
            quantity=db_trade.quantity,
            entry_price=db_trade.entry_price,
            current_price=db_trade.entry_price,
            stop_loss=db_trade.stop_loss,
            target=db_trade.target,
            realized_pnl=0.0,
        )

        db.add(db_position)
        db.commit()
        db.refresh(db_position)

        return db_trade

    @staticmethod
    def close_trade(
        db: Session,
        trade_id: int,
        exit_price: float,
    ):

        trade = (
            db.query(PaperTrade)
            .filter(PaperTrade.id == trade_id)
            .first()
        )

        if trade is None:
            return None

        if trade.status == "CLOSED":
            return trade

        pnl = PnLService.calculate_realized_pnl(
            side=trade.trade_type,
            entry_price=trade.entry_price,
            exit_price=exit_price,
            quantity=trade.quantity,
        )

        trade.exit_price = exit_price
        trade.pnl = pnl
        trade.status = "CLOSED"
        trade.closed_at = datetime.utcnow()

        db.commit()
        db.refresh(trade)

        return trade

    @staticmethod
    def get_all_trades(
        db: Session,
        status: str | None = None,
        symbol: str | None = None,
        strategy: str | None = None,
        from_date=None,
        to_date=None,
        limit: int = 20,
        offset: int = 0,
    ):

        query = db.query(PaperTrade)

        if status:
            query = query.filter(
                PaperTrade.status == status
            )

        if symbol:
            query = query.filter(
                PaperTrade.symbol == symbol
            )

        if strategy:
            query = query.filter(
                PaperTrade.strategy == strategy
            )

        if from_date:
            query = query.filter(
                PaperTrade.created_at >= from_date
            )

        if to_date:
            query = query.filter(
                PaperTrade.created_at <= to_date
            )

        return (
            query
            .order_by(PaperTrade.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )