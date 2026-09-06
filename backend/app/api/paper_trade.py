from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.paper_trading.engine import PaperTradingEngine
from app.schemas.close_trade import CloseTradeRequest
from app.schemas.paper_trade import (
    PaperTradeCreate,
    PaperTradeResponse,
)
from app.services.position_service import PositionService


router = APIRouter(
    prefix="/paper-trade",
    tags=["Paper Trading"],
)


# =========================================================
# GET ALL PAPER TRADES
# =========================================================

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

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

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


# =========================================================
# CREATE PAPER TRADE
# =========================================================

@router.post(
    "/",
    response_model=PaperTradeResponse,
)
def create_trade(
    trade: PaperTradeCreate,
    db: Session = Depends(get_db),
):
    try:

        return PaperTradingEngine.create_trade(
            db=db,
            trade=trade,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )


# =========================================================
# MONITOR OPEN PAPER POSITIONS
# =========================================================

@router.post("/monitor")
def monitor_paper_positions(
    db: Session = Depends(get_db),
):
    try:

        return PositionService.monitor_positions(
            db
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# CLOSE PAPER TRADE
# =========================================================

@router.post(
    "/{trade_id}/close",
    response_model=PaperTradeResponse,
)
def close_trade(
    trade_id: int,
    request: CloseTradeRequest,
    db: Session = Depends(get_db),
):
    try:

        trade = PaperTradingEngine.close_trade(
            db=db,
            trade_id=trade_id,
            exit_price=request.exit_price,
            exit_reason="MANUAL",
        )

        if trade is None:

            raise HTTPException(
                status_code=404,
                detail="Paper trade not found.",
            )

        return trade

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )