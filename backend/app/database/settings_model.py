from sqlalchemy import Column, Integer, Float

from app.database.database import Base


class PortfolioSettings(Base):

    __tablename__ = "portfolio_settings"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    starting_capital = Column(
        Float,
        nullable=False,
        default=20000.0,
    )