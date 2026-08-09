from app.database.database import SessionLocal
from app.services.portfolio_service import PortfolioService


db = SessionLocal()

try:
    summary = PortfolioService.get_portfolio_summary(db)

    print("\nPORTFOLIO SUMMARY")
    print("------------------")

    for key, value in summary.items():
        print(f"{key}: {value}")

finally:
    db.close()