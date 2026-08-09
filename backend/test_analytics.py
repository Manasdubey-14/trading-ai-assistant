from app.database.database import SessionLocal
from app.services.analytics_service import AnalyticsService


db = SessionLocal()

try:

    result = AnalyticsService.get_market_health(db)

    print("\nMARKET HEALTH")
    print("=" * 50)

    print(result)

finally:

    db.close()