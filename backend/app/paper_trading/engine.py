from sqlalchemy.orm import Session

from app.database.trade_models import PaperTrade


class PaperTradingEngine:

    @staticmethod
    def create_trade(db: Session, trade):

        db_trade = PaperTrade(
            symbol=trade.symbol,
            trade_type=trade.trade_type,
            quantity=trade.quantity,
            entry_price=trade.entry_price,
            stop_loss=trade.stop_loss,
            target=trade.target,
        )

        db.add(db_trade)
        db.commit()
        db.refresh(db_trade)

        return db_trade
    @staticmethod
    def close_trade(
        db: Session,
        trade_id: int,
        exit_price: float,
    ):
        """
        Close a paper trade and calculate P&L.
        """

        trade = (
            db.query(PaperTrade)
            .filter(PaperTrade.id == trade_id)
            .first()
        )

        if trade is None:
            return None

        if trade.status == "CLOSED":
            return trade

        trade.exit_price = exit_price

        trade.pnl = (
            exit_price - trade.entry_price
        ) * trade.quantity

        trade.status = "CLOSED"

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
            query = query.filter(PaperTrade.status == status)

        if symbol:
            query = query.filter(PaperTrade.symbol == symbol)

        if strategy:
            query = query.filter(PaperTrade.strategy == strategy)

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