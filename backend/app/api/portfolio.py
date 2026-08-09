from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.portfolio import PortfolioResponse
from app.services.portfolio_service import PortfolioService
from app.services.position_service import PositionService

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


@router.get("/", response_model=PortfolioResponse)
def get_portfolio(
    db: Session = Depends(get_db),
):
    return PortfolioService.get_portfolio_summary(db)
@router.get("/positions")
def get_positions(
    db: Session = Depends(get_db),
):
    return PositionService.get_positions(db)