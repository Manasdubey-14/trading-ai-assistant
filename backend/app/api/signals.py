from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.signal_service import SignalService

router = APIRouter(
    prefix="/signals",
    tags=["Signals"],
)


@router.get("/latest")
def latest_signals(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return SignalService.get_latest_signals(
        db,
        limit,
    )