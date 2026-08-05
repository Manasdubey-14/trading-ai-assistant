from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.paper_trading.engine import PaperTradingEngine
from app.schemas.paper_trade import (
    PaperTradeCreate,
    PaperTradeResponse,
)
from app.schemas.close_trade import CloseTradeRequest
from datetime import datetime

router = APIRouter(
    prefix="/paper-trade",
    tags=["Paper Trading"],
)
@router.get(
    "/",
    response_model=list[PaperTradeResponse],
)
def get_all_trades(
    status: str | None = Query(default=None),
    symbol: str | None = Query(default=None),
    strategy: str | None = Query(default=None),

    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),

    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),

    db: Session = Depends(get_db),
):
    return PaperTradingEngine.get_all_trades(
        db=db,
        status=status,
        symbol=symbol,
        strategy=strategy,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )

@router.post("/")
def create_trade(
    trade: PaperTradeCreate,
    db: Session = Depends(get_db),
):
    return PaperTradingEngine.create_trade(db, trade)
@router.post("/{trade_id}/close")
def close_trade(
    trade_id: int,
    request: CloseTradeRequest,
    db: Session = Depends(get_db),
):
    trade = PaperTradingEngine.close_trade(
        db=db,
        trade_id=trade_id,
        exit_price=request.exit_price,
    )

    if trade is None:
        return {
            "error": "Trade not found."
        }

    return trade