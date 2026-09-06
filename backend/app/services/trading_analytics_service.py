from collections import defaultdict

from sqlalchemy.orm import Session

from app.database.trade_models import PaperTrade


class TradingAnalyticsService:
    @staticmethod
    def _build_performance_breakdown(
        trades,
        attribute,
    ):
        grouped_trades = defaultdict(list)

        for trade in trades:

            name = (
                getattr(trade, attribute)
                or "UNKNOWN"
            )

            grouped_trades[name].append(
                trade
            )

        breakdown = {}

        for name, group in grouped_trades.items():

            pnls = [
                float(trade.pnl or 0)
                for trade in group
            ]

            wins = [
                pnl
                for pnl in pnls
                if pnl > 0
            ]

            losses = [
                pnl
                for pnl in pnls
                if pnl < 0
            ]

            gross_profit = sum(wins)

            gross_loss = abs(
                sum(losses)
            )

            target_hits = sum(
                1
                for trade in group
                if trade.exit_reason == "TARGET"
            )

            stop_loss_hits = sum(
                1
                for trade in group
                if trade.exit_reason == "STOP_LOSS"
            )

            manual_exits = sum(
                1
                for trade in group
                if trade.exit_reason == "MANUAL"
            )

            breakdown[name] = {
                "trades": len(group),

                "wins": len(wins),

                "losses": len(losses),

                "win_rate": round(
                    len(wins)
                    / len(group)
                    * 100,
                    2,
                ),

                "total_pnl": round(
                    sum(pnls),
                    2,
                ),

                "gross_profit": round(
                    gross_profit,
                    2,
                ),

                "gross_loss": round(
                    gross_loss,
                    2,
                ),

                "profit_factor": round(
                    gross_profit
                    / gross_loss,
                    2,
                )
                if gross_loss > 0
                else 0.0,

                "average_win": round(
                    gross_profit
                    / len(wins),
                    2,
                )
                if wins
                else 0.0,

                "average_loss": round(
                    gross_loss
                    / len(losses),
                    2,
                )
                if losses
                else 0.0,

                "best_trade": round(
                    max(pnls),
                    2,
                ),

                "worst_trade": round(
                    min(pnls),
                    2,
                ),

                "target_hits": target_hits,

                "stop_loss_hits": stop_loss_hits,

                "manual_exits": manual_exits,
            }

        return breakdown

    @staticmethod
    def get_summary(db: Session):

        trades = (
            db.query(PaperTrade)
            .filter(
                PaperTrade.status == "CLOSED"
            )
            .order_by(
                PaperTrade.closed_at.asc()
            )
            .all()
        )

        total_trades = len(trades)

        if total_trades == 0:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "gross_profit": 0.0,
                "gross_loss": 0.0,
                "profit_factor": 0.0,
                "average_win": 0.0,
                "average_loss": 0.0,
                "best_trade": 0.0,
                "worst_trade": 0.0,
                "maximum_drawdown": 0.0,
                "maximum_drawdown_percent": 0.0,
                "current_streak": 0,
                "current_streak_type": None,
                "best_winning_streak": 0,
                "worst_losing_streak": 0,
                "exit_reason_breakdown": {},
                "strategy_breakdown": {},
                "timeframe_breakdown": {},
                "daily_pnl": [],
                "cumulative_pnl": [],
            }

        # =====================================================
        # BASIC P&L
        # =====================================================

        winning_trades = [
            trade
            for trade in trades
            if (trade.pnl or 0) > 0
        ]

        losing_trades = [
            trade
            for trade in trades
            if (trade.pnl or 0) < 0
        ]

        total_pnl = sum(
            trade.pnl or 0
            for trade in trades
        )

        gross_profit = sum(
            trade.pnl or 0
            for trade in winning_trades
        )

        gross_loss = abs(
            sum(
                trade.pnl or 0
                for trade in losing_trades
            )
        )

        win_rate = (
            len(winning_trades)
            / total_trades
            * 100
        )

        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0
            else 0.0
        )

        average_win = (
            gross_profit / len(winning_trades)
            if winning_trades
            else 0.0
        )

        average_loss = (
            gross_loss / len(losing_trades)
            if losing_trades
            else 0.0
        )

        best_trade = max(
            trade.pnl or 0
            for trade in trades
        )

        worst_trade = min(
            trade.pnl or 0
            for trade in trades
        )

        # =====================================================
        # CUMULATIVE P&L + MAX DRAWDOWN
        # =====================================================

        cumulative_pnl = []

        running_pnl = 0.0
        peak_pnl = 0.0
        maximum_drawdown = 0.0

        for trade in trades:

            pnl = float(trade.pnl or 0)

            running_pnl += pnl

            if running_pnl > peak_pnl:
                peak_pnl = running_pnl

            drawdown = peak_pnl - running_pnl

            if drawdown > maximum_drawdown:
                maximum_drawdown = drawdown

            cumulative_pnl.append({
                "trade_id": trade.id,
                "closed_at": (
                    trade.closed_at.isoformat()
                    if trade.closed_at
                    else None
                ),
                "pnl": round(
                    pnl,
                    2,
                ),
                "cumulative_pnl": round(
                    running_pnl,
                    2,
                ),
            })

        maximum_drawdown_percent = (
            maximum_drawdown / peak_pnl * 100
            if peak_pnl > 0
            else 0.0
        )

        # =====================================================
        # WIN / LOSS STREAK
        # =====================================================

        current_streak = 0
        current_streak_type = None

        best_winning_streak = 0
        worst_losing_streak = 0

        winning_streak = 0
        losing_streak = 0

        for trade in trades:

            pnl = float(trade.pnl or 0)

            if pnl > 0:

                winning_streak += 1
                losing_streak = 0

                if winning_streak > best_winning_streak:
                    best_winning_streak = (
                        winning_streak
                    )

            elif pnl < 0:

                losing_streak += 1
                winning_streak = 0

                if losing_streak > worst_losing_streak:
                    worst_losing_streak = (
                        losing_streak
                    )

            else:

                winning_streak = 0
                losing_streak = 0

        if trades:

            last_pnl = float(
                trades[-1].pnl or 0
            )

            if last_pnl > 0:

                current_streak_type = "WIN"

                for trade in reversed(trades):

                    if (trade.pnl or 0) > 0:
                        current_streak += 1
                    else:
                        break

            elif last_pnl < 0:

                current_streak_type = "LOSS"

                for trade in reversed(trades):

                    if (trade.pnl or 0) < 0:
                        current_streak += 1
                    else:
                        break

        # =====================================================
        # EXIT REASON BREAKDOWN
        # =====================================================

        exit_reason_breakdown = defaultdict(
            lambda: {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "total_pnl": 0.0,
            }
        )

        for trade in trades:

            reason = (
                trade.exit_reason
                or "UNKNOWN"
            )

            pnl = float(
                trade.pnl or 0
            )

            data = exit_reason_breakdown[
                reason
            ]

            data["trades"] += 1
            data["total_pnl"] += pnl

            if pnl > 0:
                data["wins"] += 1

            elif pnl < 0:
                data["losses"] += 1

        for data in exit_reason_breakdown.values():

            data["total_pnl"] = round(
                data["total_pnl"],
                2,
            )

        # =====================================================
        # STRATEGY PERFORMANCE
        # =====================================================

        strategy_breakdown = (
            TradingAnalyticsService
            ._build_performance_breakdown(
                trades,
                "strategy",
            )
        )

        # =====================================================
        # TIMEFRAME PERFORMANCE
        # =====================================================

        timeframe_breakdown = (
            TradingAnalyticsService
            ._build_performance_breakdown(
                trades,
                "timeframe",
            )
        )

        # =====================================================
        # DAILY P&L
        # =====================================================

        daily_pnl = defaultdict(float)

        for trade in trades:

            if trade.closed_at:

                day = (
                    trade.closed_at
                    .date()
                    .isoformat()
                )

                daily_pnl[day] += float(
                    trade.pnl or 0
                )

        daily_pnl_result = [
            {
                "date": date,
                "pnl": round(
                    pnl,
                    2,
                ),
            }
            for date, pnl
            in sorted(
                daily_pnl.items()
            )
        ]

        # =====================================================
        # FINAL RESPONSE
        # =====================================================

        return {
            "total_trades": total_trades,

            "winning_trades": len(
                winning_trades
            ),

            "losing_trades": len(
                losing_trades
            ),

            "win_rate": round(
                win_rate,
                2,
            ),

            "total_pnl": round(
                total_pnl,
                2,
            ),

            "gross_profit": round(
                gross_profit,
                2,
            ),

            "gross_loss": round(
                gross_loss,
                2,
            ),

            "profit_factor": round(
                profit_factor,
                2,
            ),

            "average_win": round(
                average_win,
                2,
            ),

            "average_loss": round(
                average_loss,
                2,
            ),

            "best_trade": round(
                best_trade,
                2,
            ),

            "worst_trade": round(
                worst_trade,
                2,
            ),

            "maximum_drawdown": round(
                maximum_drawdown,
                2,
            ),

            "maximum_drawdown_percent": round(
                maximum_drawdown_percent,
                2,
            ),

            "current_streak": current_streak,

            "current_streak_type": (
                current_streak_type
            ),

            "best_winning_streak": (
                best_winning_streak
            ),

            "worst_losing_streak": (
                worst_losing_streak
            ),

            "exit_reason_breakdown": dict(
                exit_reason_breakdown
            ),

            "strategy_breakdown": dict(
                strategy_breakdown
            ),

            "timeframe_breakdown": dict(
                timeframe_breakdown
            ),

            "daily_pnl": daily_pnl_result,

            "cumulative_pnl": cumulative_pnl,
        }