from app.database.database import SessionLocal
from app.services.dashboard_service import DashboardService

db = SessionLocal()

try:
    summary = DashboardService.get_summary(db)

    print(summary)

finally:
    db.close()