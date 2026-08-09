class PnLService:

    @staticmethod
    def calculate_unrealized_pnl(
        side: str,
        entry_price: float,
        current_price: float,
        quantity: int,
    ) -> float:

        if side.upper() == "BUY":

            pnl = (
                current_price - entry_price
            ) * quantity

        elif side.upper() == "SELL":

            pnl = (
                entry_price - current_price
            ) * quantity

        else:

            raise ValueError(
                "Side must be BUY or SELL"
            )

        return round(pnl, 2)

    @staticmethod
    def calculate_realized_pnl(
        side: str,
        entry_price: float,
        exit_price: float,
        quantity: int,
    ) -> float:

        if side.upper() == "BUY":

            pnl = (
                exit_price - entry_price
            ) * quantity

        elif side.upper() == "SELL":

            pnl = (
                entry_price - exit_price
            ) * quantity

        else:

            raise ValueError(
                "Side must be BUY or SELL"
            )

        return round(pnl, 2)