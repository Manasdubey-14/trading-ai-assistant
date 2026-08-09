from app.database.database import SessionLocal
from app.services.dashboard_service import DashboardService

db = SessionLocal()

try:
    dashboard = DashboardService.get_dashboard(db)

    print(dashboard)

finally:
    db.close()