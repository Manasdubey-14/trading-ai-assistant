import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.calendar import router as calendar_router
from app.api.dashboard import router as dashboard_router
from app.api.decision import router as decision_router
from app.api.opportunities import router as opportunities_router
from app.api.paper_trade import router as paper_trade_router
from app.api.portfolio import router as portfolio_router
from app.api.scanner import router as scanner_router
from app.api.settings import router as settings_router
from app.api.signals import router as signals_router
from app.api.stock import router as stock_router

from app.database.database import Base, engine
from app.database import models
from app.database import trade_models
from app.database.position_model import Position
from app.database.settings_model import PortfolioSettings
from app.database.signal_model import MarketSignal

from app.services.paper_trading_monitor import PaperTradingMonitor
from app.api.analytics import router as analytics_router
from app.api.backtest import router as backtest_router


Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Start background paper-trading monitor
    monitor_task = asyncio.create_task(
        PaperTradingMonitor.run_loop()
    )

    print(
        "[Paper Monitor] "
        "Background monitor task started."
    )

    try:
        yield

    finally:
        # Stop background monitor cleanly
        monitor_task.cancel()

        with suppress(asyncio.CancelledError):
            await monitor_task

        print(
            "[Paper Monitor] "
            "Background monitor stopped."
        )


app = FastAPI(
    title="Trading AI Assistant",
    version="1.0.0",
    description="AI-powered Trading Assistant Backend",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(settings_router)
app.include_router(analytics_router)
app.include_router(backtest_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Trading AI Assistant 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }