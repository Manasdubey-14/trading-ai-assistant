from app.database.database import SessionLocal
from app.database.position_model import Position
from app.services.position_service import PositionService


db = SessionLocal()


position = Position(
    symbol="RELIANCE.NS",
    side="BUY",
    quantity=10,
    entry_price=1297.00,
    current_price=1310.00,
    stop_loss=1284.00,
    target=1323.00,
)

db.add(position)
db.commit()
db.refresh(position)


positions = PositionService.get_positions(db)


for item in positions:
    print(item)


db.close()