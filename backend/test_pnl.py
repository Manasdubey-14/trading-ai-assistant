from app.services.pnl_service import PnLService


# =========================
# UNREALIZED P&L
# =========================

long_unrealized = PnLService.calculate_unrealized_pnl(
    side="BUY",
    entry_price=1000,
    current_price=1050,
    quantity=10,
)

short_unrealized = PnLService.calculate_unrealized_pnl(
    side="SELL",
    entry_price=1000,
    current_price=950,
    quantity=10,
)


# =========================
# REALIZED P&L
# =========================

long_realized = PnLService.calculate_realized_pnl(
    side="BUY",
    entry_price=1000,
    exit_price=1050,
    quantity=10,
)

short_realized = PnLService.calculate_realized_pnl(
    side="SELL",
    entry_price=1000,
    exit_price=950,
    quantity=10,
)


# =========================
# RESULTS
# =========================

print("Long Unrealized P&L:", long_unrealized)
print("Short Unrealized P&L:", short_unrealized)

print("Long Realized P&L:", long_realized)
print("Short Realized P&L:", short_realized)