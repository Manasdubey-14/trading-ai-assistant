from pydantic import BaseModel

from app.schemas.dashboard import DashboardSummary
from app.schemas.signal import SignalResponse
from app.schemas.opportunity import Opportunity
from app.schemas.analytics import MarketAnalytics
from app.schemas.portfolio import PortfolioResponse


class DashboardResponse(BaseModel):

    summary: DashboardSummary

    latest_signals: list[SignalResponse]

    top_opportunities: list[Opportunity]

    market_health: MarketAnalytics

    portfolio: PortfolioResponse