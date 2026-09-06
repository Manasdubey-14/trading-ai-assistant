from datetime import datetime

from sqlalchemy.orm import Session

from app.database.position_model import Position
from app.database.trade_models import PaperTrade
from app.services.market_data import MarketDataService
from app.services.pnl_service import PnLService


class PaperTradingEngine:

    @staticmethod
    def create_trade(
        db: Session,
        trade,
    ):
        symbol = trade.symbol.strip().upper()
        trade_type = trade.trade_type.strip().upper()

        if trade_type not in {"BUY", "SELL"}:
            raise ValueError(
                "trade_type must be BUY or SELL"
            )

        if trade.quantity <= 0:
            raise ValueError(
                "quantity must be greater than zero"
            )

        # -----------------------------------------
        # GET CURRENT MARKET PRICE
        # -----------------------------------------

        entry_price = trade.entry_price

        if entry_price is None:

            market_data = MarketDataService.get_stock_data(
                symbol
            )

            entry_price = market_data.get(
                "current_price"
            )

            if entry_price is None:
                raise ValueError(
                    f"Unable to get current market price for {symbol}"
                )

            entry_price = float(entry_price)

        if entry_price <= 0:
            raise ValueError(
                "entry_price must be greater than zero"
            )

        # -----------------------------------------
        # VALIDATE STOP LOSS / TARGET
        # -----------------------------------------

        if trade.stop_loss <= 0:
            raise ValueError(
                "stop_loss must be greater than zero"
            )

        if trade.target <= 0:
            raise ValueError(
                "target must be greater than zero"
            )

        if trade_type == "BUY":

            if trade.stop_loss >= entry_price:
                raise ValueError(
                    "For BUY trades, stop_loss must be below entry_price."
                )

            if trade.target <= entry_price:
                raise ValueError(
                    "For BUY trades, target must be above entry_price."
                )

        elif trade_type == "SELL":

            if trade.stop_loss <= entry_price:
                raise ValueError(
                    "For SELL trades, stop_loss must be above entry_price."
                )

            if trade.target >= entry_price:
                raise ValueError(
                    "For SELL trades, target must be below entry_price."
                )

        # -----------------------------------------
        # CREATE PAPER TRADE
        # -----------------------------------------

        db_trade = PaperTrade(
            symbol=symbol,
            trade_type=trade_type,
            quantity=trade.quantity,
            entry_price=entry_price,
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

        # -----------------------------------------
        # CREATE LINKED POSITION
        # -----------------------------------------

        db_position = Position(
            paper_trade_id=db_trade.id,
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
        exit_reason: str = "MANUAL",
    ):
        trade = (
            db.query(PaperTrade)
            .filter(
                PaperTrade.id == trade_id
            )
            .first()
        )

        if trade is None:
            return None

        if trade.status == "CLOSED":
            return trade

        if exit_price <= 0:
            raise ValueError(
                "exit_price must be greater than zero"
            )

        allowed_reasons = {
            "MANUAL",
            "STOP_LOSS",
            "TARGET",
        }

        exit_reason = exit_reason.upper()

        if exit_reason not in allowed_reasons:
            raise ValueError(
                "exit_reason must be MANUAL, STOP_LOSS, or TARGET"
            )

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
        trade.exit_reason = exit_reason

        position = (
            db.query(Position)
            .filter(
                Position.paper_trade_id == trade.id
            )
            .first()
        )

        if position is not None:
            db.delete(position)

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
            .order_by(
                PaperTrade.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )