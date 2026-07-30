from fastapi import APIRouter
from app.services.market_data import MarketDataService
from app.schemas.stock import EMAResponse

router = APIRouter(
    prefix="/stock",
    tags=["Stock"],
)


@router.get("/{symbol}")
def get_stock(symbol: str):
    return MarketDataService.get_stock_data(symbol)


@router.get("/{symbol}/history")
def get_history(
    symbol: str,
    period: str = "6mo",
    interval: str = "1d",
):
    return MarketDataService.get_history(
        symbol,
        period,
        interval,
    )
@router.get("/{symbol}/ema")
def get_ema(
    symbol: str,
    period: int = 20,
    interval: str = "1d",
):
    return MarketDataService.get_ema(
        symbol,
        period,
        interval,
    )
@router.get("/{symbol}/ema", response_model=EMAResponse)
def get_ema(
    symbol: str,
    period: int = 20,
    interval: str = "1d",
):
    return MarketDataService.get_ema(
        symbol,
        period,
        interval,
    )