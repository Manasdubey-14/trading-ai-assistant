from sqlalchemy.orm import Session

from app.database.settings_model import PortfolioSettings


class SettingsService:

    @staticmethod
    def get_portfolio_settings(db: Session):

        settings = (
            db.query(PortfolioSettings)
            .first()
        )

        if settings is None:

            settings = PortfolioSettings(
                starting_capital=20000.0
            )

            db.add(settings)
            db.commit()
            db.refresh(settings)

        return settings

    @staticmethod
    def update_starting_capital(
        db: Session,
        starting_capital: float,
    ):

        settings = (
            db.query(PortfolioSettings)
            .first()
        )

        if settings is None:

            settings = PortfolioSettings(
                starting_capital=starting_capital
            )

            db.add(settings)

        else:

            settings.starting_capital = starting_capital

        db.commit()
        db.refresh(settings)

        return settings