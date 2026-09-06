from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.market.scanner import MarketScanner


router = APIRouter(
    prefix="/scanner",
    tags=["Market Scanner"],
)


@router.get("/")
def scan_market():
    return MarketScanner.scan()


@router.post("/save")
def scan_and_save(
    db: Session = Depends(get_db),
):
    return MarketScanner.scan_and_save(db)