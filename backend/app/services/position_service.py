from sqlalchemy.orm import Session

from app.database.position_model import Position
from app.services.pnl_service import PnLService


class PositionService:

    @staticmethod
    def get_positions(db: Session):

        positions = (
            db.query(Position)
            .order_by(Position.created_at.desc())
            .all()
        )

        results = []

        for position in positions:

            unrealized_pnl = (
                PnLService.calculate_unrealized_pnl(
                    side=position.side,
                    entry_price=position.entry_price,
                    current_price=position.current_price,
                    quantity=position.quantity,
                )
            )

            results.append({
                "id": position.id,
                "paper_trade_id": position.paper_trade_id,
                "symbol": position.symbol,
                "side": position.side,
                "quantity": position.quantity,
                "entry_price": position.entry_price,
                "current_price": position.current_price,
                "stop_loss": position.stop_loss,
                "target": position.target,
                "unrealized_pnl": unrealized_pnl,
                "realized_pnl": position.realized_pnl or 0.0,
                "created_at": position.created_at,
                "updated_at": position.updated_at,
            })

        return results

    @staticmethod
    def update_current_prices(db: Session):

        from app.services.market_data import MarketDataService

        positions = (
            db.query(Position)
            .order_by(Position.created_at.desc())
            .all()
        )

        updated = []

        for position in positions:

            try:
                market_data = (
                    MarketDataService.get_stock_data(
                        position.symbol
                    )
                )

                current_price = market_data.get(
                    "current_price"
                )

                if current_price is None:
                    print(
                        f"No current price for "
                        f"{position.symbol}"
                    )
                    continue

                position.current_price = float(
                    current_price
                )

                updated.append({
                    "id": position.id,
                    "symbol": position.symbol,
                    "current_price": position.current_price,
                })

            except Exception as exc:
                print(
                    f"Price update failed for "
                    f"{position.symbol}: {exc}"
                )

        db.commit()

        return updated
    @staticmethod
    def monitor_positions(db: Session):

        from app.paper_trading.engine import PaperTradingEngine
        from app.services.market_data import MarketDataService

        positions = (
            db.query(Position)
            .order_by(Position.created_at.desc())
            .all()
        )

        updated_positions = []
        triggered_positions = []

        for position in positions:

            try:
                market_data = MarketDataService.get_stock_data(
                    position.symbol
                )

                current_price = market_data.get(
                    "current_price"
                )

                if current_price is None:
                    continue

                current_price = float(current_price)

                position.current_price = current_price

                should_close = False

                if position.side.upper() == "BUY":

                    if (
                        position.stop_loss is not None
                        and current_price <= position.stop_loss
                    ):
                        should_close = True

                    elif (
                        position.target is not None
                        and current_price >= position.target
                    ):
                        should_close = True

                elif position.side.upper() == "SELL":

                    if (
                        position.stop_loss is not None
                        and current_price >= position.stop_loss
                    ):
                        should_close = True

                    elif (
                        position.target is not None
                        and current_price <= position.target
                    ):
                        should_close = True

                updated_positions.append({
                    "id": position.id,
                    "paper_trade_id": position.paper_trade_id,
                    "symbol": position.symbol,
                    "side": position.side,
                    "current_price": current_price,
                    "stop_loss": position.stop_loss,
                    "target": position.target,
                    "triggered": should_close,
                })

                if should_close:

                    exit_reason = "MANUAL"

                    if position.side.upper() == "BUY":

                        if (
                            position.stop_loss is not None
                            and current_price <= position.stop_loss
                        ):
                            exit_reason = "STOP_LOSS"

                        elif (
                            position.target is not None
                            and current_price >= position.target
                        ):
                            exit_reason = "TARGET"

                    elif position.side.upper() == "SELL":

                        if (
                            position.stop_loss is not None
                            and current_price >= position.stop_loss
                        ):
                            exit_reason = "STOP_LOSS"

                        elif (
                            position.target is not None
                            and current_price <= position.target
                        ):
                            exit_reason = "TARGET"

                    trade = PaperTradingEngine.close_trade(
                        db=db,
                        trade_id=position.paper_trade_id,
                        exit_price=current_price,
                        exit_reason=exit_reason,
                    )

                    if trade is not None:
                        triggered_positions.append({
                            "position_id": position.id,
                            "paper_trade_id": position.paper_trade_id,
                            "symbol": position.symbol,
                            "exit_price": current_price,
                            "pnl": trade.pnl,
                            "status": trade.status,
                            "exit_reason": trade.exit_reason,
                        })

            except Exception as exc:

                print(
                    f"Position monitoring failed for "
                    f"{position.symbol}: {exc}"
                )

        db.commit()

        return {
            "updated_positions": updated_positions,
            "triggered_positions": triggered_positions,
        }