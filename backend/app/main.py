from fastapi import FastAPI
from app.api.stock import router as stock_router
from app.database.database import Base
from app.database.position_model import Position
from app.database.database import engine
from app.database import models
from app.database import trade_models
from app.api.paper_trade import router as paper_trade_router
from app.api.portfolio import router as portfolio_router
from app.api.decision import router as decision_router
from app.api.scanner import router as scanner_router
from app.database.signal_model import MarketSignal
from app.api.signals import router as signals_router
from app.api.dashboard import router as dashboard_router
from app.api.opportunities import router as opportunities_router
from app.api.calendar import router as calendar_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trading AI Assistant",
    version="1.0.0",
    description="AI-powered Trading Assistant Backend"
)

app.include_router(stock_router)
app.include_router(paper_trade_router)
app.include_router(portfolio_router)
app.include_router(decision_router)
app.include_router(scanner_router)
app.include_router(signals_router)
app.include_router(dashboard_router)
app.include_router(opportunities_router)
app.include_router(calendar_router)

@app.get("/")
def root():
    return {"message": "Welcome to Trading AI Assistant 🚀"}


@app.get("/health")
def health():
    return {"status": "healthy"}