from app.database.database import SessionLocal
from app.services.opportunity_service import OpportunityService

db = SessionLocal()

try:

    opportunities = OpportunityService.get_top_opportunities(db)

    for opportunity in opportunities:

        print(opportunity)

finally:

    db.close()