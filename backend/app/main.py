from fastapi import FastAPI
from app.api.stock import router as stock_router
from app.database.database import Base
from app.database.database import engine
from app.database import models
from app.database import trade_models
from app.api.paper_trade import router as paper_trade_router
from app.api.portfolio import router as portfolio_router
from app.api.decision import router as decision_router

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

@app.get("/")
def root():
    return {"message": "Welcome to Trading AI Assistant 🚀"}


@app.get("/health")
def health():
    return {"status": "healthy"}