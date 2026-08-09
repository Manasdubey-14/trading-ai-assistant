from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.opportunity_service import OpportunityService


router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"],
)


@router.get("/")
def get_opportunities(
    db: Session = Depends(get_db),
):
    return OpportunityService.get_top_opportunities(db)