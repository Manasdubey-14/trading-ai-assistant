from collections import defaultdict


class BacktestAnalytics:

    @staticmethod
    def calculate(trades):

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
                "symbol_breakdown": {},
                "side_breakdown": {},
                "exit_reason_breakdown": {},
                "score_breakdown": {},
                "cumulative_pnl": [],
            }

        # =====================================================
        # BASIC P&L
        # =====================================================

        winning_trades = [
            trade
            for trade in trades
            if trade["pnl"] > 0
        ]

        losing_trades = [
            trade
            for trade in trades
            if trade["pnl"] < 0
        ]

        total_pnl = sum(
            trade["pnl"]
            for trade in trades
        )

        gross_profit = sum(
            trade["pnl"]
            for trade in winning_trades
        )

        gross_loss = abs(
            sum(
                trade["pnl"]
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
            gross_profit
            / len(winning_trades)
            if winning_trades
            else 0.0
        )

        average_loss = (
            gross_loss
            / len(losing_trades)
            if losing_trades
            else 0.0
        )

        best_trade = max(
            trade["pnl"]
            for trade in trades
        )

        worst_trade = min(
            trade["pnl"]
            for trade in trades
        )

        # =====================================================
        # CUMULATIVE P&L / DRAWDOWN
        # =====================================================

        cumulative_pnl = []

        running_pnl = 0.0
        peak_pnl = 0.0
        maximum_drawdown = 0.0

        for trade in trades:

            pnl = float(
                trade["pnl"]
            )

            running_pnl += pnl

            if running_pnl > peak_pnl:
                peak_pnl = running_pnl

            drawdown = (
                peak_pnl
                - running_pnl
            )

            if drawdown > maximum_drawdown:
                maximum_drawdown = drawdown

            cumulative_pnl.append({
                "trade_id": trade["trade_id"],
                "exit_date": trade["exit_date"],
                "pnl": round(pnl, 2),
                "cumulative_pnl": round(
                    running_pnl,
                    2,
                ),
            })

        maximum_drawdown_percent = (
            maximum_drawdown
            / peak_pnl
            * 100
            if peak_pnl > 0
            else 0.0
        )

        # =====================================================
        # SYMBOL BREAKDOWN
        # =====================================================

        symbol_breakdown = defaultdict(
            lambda: {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "total_pnl": 0.0,
            }
        )

        for trade in trades:

            symbol = trade["symbol"]

            data = symbol_breakdown[
                symbol
            ]

            data["trades"] += 1
            data["total_pnl"] += trade["pnl"]

            if trade["pnl"] > 0:
                data["wins"] += 1

            elif trade["pnl"] < 0:
                data["losses"] += 1

        for data in symbol_breakdown.values():

            data["total_pnl"] = round(
                data["total_pnl"],
                2,
            )

        # =====================================================
        # BUY / SELL BREAKDOWN
        # =====================================================

        side_breakdown = defaultdict(
            lambda: {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "total_pnl": 0.0,
            }
        )

        for trade in trades:

            side = trade["side"]

            data = side_breakdown[side]

            data["trades"] += 1
            data["total_pnl"] += trade["pnl"]

            if trade["pnl"] > 0:
                data["wins"] += 1

            elif trade["pnl"] < 0:
                data["losses"] += 1

        for data in side_breakdown.values():

            data["total_pnl"] = round(
                data["total_pnl"],
                2,
            )

        # =====================================================
        # EXIT REASON
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

            reason = trade["exit_reason"]

            data = (
                exit_reason_breakdown[
                    reason
                ]
            )

            data["trades"] += 1
            data["total_pnl"] += trade["pnl"]

            if trade["pnl"] > 0:
                data["wins"] += 1

            elif trade["pnl"] < 0:
                data["losses"] += 1

        for data in exit_reason_breakdown.values():

            data["total_pnl"] = round(
                data["total_pnl"],
                2,
            )

        # =====================================================
        # SIGNAL SCORE BREAKDOWN
        # =====================================================

        score_breakdown = defaultdict(
            lambda: {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "total_pnl": 0.0,
            }
        )

        for trade in trades:

            score = str(
                trade["signal_score"]
            )

            data = score_breakdown[
                score
            ]

            data["trades"] += 1
            data["total_pnl"] += trade["pnl"]

            if trade["pnl"] > 0:
                data["wins"] += 1

            elif trade["pnl"] < 0:
                data["losses"] += 1

        for data in score_breakdown.values():

            data["total_pnl"] = round(
                data["total_pnl"],
                2,
            )

        # =====================================================
        # FINAL RESULT
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

            "symbol_breakdown": dict(
                symbol_breakdown
            ),

            "side_breakdown": dict(
                side_breakdown
            ),

            "exit_reason_breakdown": dict(
                exit_reason_breakdown
            ),

            "score_breakdown": dict(
                score_breakdown
            ),

            "cumulative_pnl": cumulative_pnl,
        }