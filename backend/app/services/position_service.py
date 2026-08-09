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