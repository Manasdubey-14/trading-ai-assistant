from sqlalchemy.orm import Session

from app.repositories.analytics_repository import AnalyticsRepository
from app.services.signal_service import SignalService
from app.schemas.dashboard import DashboardSummary
from app.schemas.dashboard_response import DashboardResponse
from app.services.opportunity_service import OpportunityService
from app.services.analytics_service import AnalyticsService
from app.services.portfolio_service import PortfolioService


class DashboardService:

    @staticmethod
    def get_summary(db: Session):

        total = AnalyticsRepository.total_signals(db)

        buy = AnalyticsRepository.buy_signals(db)

        sell = AnalyticsRepository.sell_signals(db)

        wait = AnalyticsRepository.wait_signals(db)

        avg_confidence = AnalyticsRepository.average_confidence(db)

        top = AnalyticsRepository.strongest_signal(db)

        return DashboardSummary(
            total_signals=total,
            buy_signals=buy,
            sell_signals=sell,
            wait_signals=wait,
            average_confidence=round(avg_confidence, 2),
            top_signal=top.symbol if top else None,
        )

    @staticmethod
    def get_dashboard(db: Session):

        summary = DashboardService.get_summary(db)

        latest_signals = SignalService.get_latest_signals(
            db=db,
            limit=10,
        )

        top_opportunities = OpportunityService.get_top_opportunities(
            db
        )

        market_health = AnalyticsService.get_market_health(
            db
        )
        portfolio = PortfolioService.get_portfolio_summary(
            db
        )

        return DashboardResponse(
            summary=summary,
            latest_signals=latest_signals,
            top_opportunities=top_opportunities,
            market_health=market_health,
            portfolio=portfolio,
        )