from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.settings import CapitalUpdate
from app.services.settings_service import SettingsService


router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
)


@router.get("/capital")
def get_capital(
    db: Session = Depends(get_db),
):
    settings = SettingsService.get_portfolio_settings(db)

    return {
        "starting_capital": settings.starting_capital
    }


@router.put("/capital")
def update_capital(
    data: CapitalUpdate,
    db: Session = Depends(get_db),
):
    settings = SettingsService.update_starting_capital(
        db=db,
        starting_capital=data.starting_capital,
    )

    return {
        "message": "Starting capital updated successfully",
        "starting_capital": settings.starting_capital,
    }