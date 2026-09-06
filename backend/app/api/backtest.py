from fastapi import APIRouter, HTTPException

from app.schemas.backtest import BacktestRequest
from app.services.market_data import MarketDataService
from app.backtesting.engine import BacktestEngine
from app.backtesting.analytics import BacktestAnalytics


router = APIRouter(
    prefix="/backtest",
    tags=["Backtesting"],
)


@router.post("/")
def run_backtest(
    request: BacktestRequest,
):
    history = MarketDataService.get_historical_data(
        symbol=request.symbol,
        period=request.period,
        interval=request.interval,
    )

    if history is None or history.empty:
        raise HTTPException(
            status_code=404,
            detail="No historical data found.",
        )

    result = BacktestEngine.run(
        symbol=request.symbol,
        history=history,
        quantity=request.quantity,
        slippage_percent=request.slippage_percent,
        transaction_cost_percent=(
            request.transaction_cost_percent
        ),
    )

    if "error" in result:
        raise HTTPException(
            status_code=400,
            detail=result["error"],
        )

    trades = result["trades"]

    summary = BacktestAnalytics.calculate(
        result["trades"]
    )

    return {
        "symbol": request.symbol,
        "period": request.period,
        "interval": request.interval,
        "quantity": request.quantity,
        "summary": summary,
        "trades": trades,
    }