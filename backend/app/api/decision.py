from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.decision import DecisionResponse
from app.schemas.execute_trade import ExecuteTradeRequest
from app.schemas.paper_trade import PaperTradeCreate
from app.services.decision_service import DecisionService
from app.engine.decision import DecisionEngine
from app.paper_trading.engine import PaperTradingEngine


router = APIRouter(
    prefix="/decision",
    tags=["Decision Engine"],
)


@router.get(
    "/{symbol}",
    response_model=DecisionResponse,
)
def analyze_stock(symbol: str):

    return DecisionService.analyze(symbol)


@router.post(
    "/{symbol}/execute",
)
def execute_decision(
    symbol: str,
    request: ExecuteTradeRequest,
    db: Session = Depends(get_db),
):

    decision = DecisionEngine.analyze(symbol)

    if decision.signal == "WAIT":
        raise HTTPException(
            status_code=400,
            detail="Cannot execute a WAIT signal.",
        )

    if decision.entry is None:
        raise HTTPException(
            status_code=400,
            detail="Decision does not contain an entry price.",
        )

    if decision.stop_loss is None:
        raise HTTPException(
            status_code=400,
            detail="Decision does not contain a stop loss.",
        )

    if decision.target is None:
        raise HTTPException(
            status_code=400,
            detail="Decision does not contain a target.",
        )

    if request.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero.",
        )

    trade = PaperTradeCreate(
        symbol=decision.symbol,
        trade_type=decision.signal,
        quantity=request.quantity,
        entry_price=decision.entry,
        stop_loss=decision.stop_loss,
        target=decision.target,
        strategy="Decision Engine",
        timeframe=None,
        confidence=decision.confidence,
        notes="Trade executed from Decision Engine",
    )

    return PaperTradingEngine.create_trade(
        db=db,
        trade=trade,
    )