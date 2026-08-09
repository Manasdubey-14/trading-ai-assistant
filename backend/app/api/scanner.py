from fastapi import APIRouter

from app.market.scanner import MarketScanner

router = APIRouter(
    prefix="/scanner",
    tags=["Market Scanner"],
)


@router.get("/")
def scan_market():
    return MarketScanner.scan()