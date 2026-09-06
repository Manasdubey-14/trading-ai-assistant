from dataclasses import dataclass

import pandas as pd

from app.analysis.ema import calculate_ema
from app.analysis.rsi import calculate_rsi
from app.analysis.macd import calculate_macd


@dataclass
class BacktestTrade:
    trade_id: int
    symbol: str
    side: str

    signal_date: str
    entry_date: str
    exit_date: str

    entry_price: float
    exit_price: float

    stop_loss: float
    target: float

    gross_pnl: float
    slippage_cost: float
    transaction_cost: float
    net_pnl: float

    # Kept for backward compatibility.
    # Existing BacktestAnalytics uses "pnl".
    pnl: float

    exit_reason: str

    signal_score: int
    confidence: float


class BacktestEngine:

    RISK_PERCENT = 0.01
    REWARD_MULTIPLIER = 2.0

    @staticmethod
    def _calculate_signal(
        ema,
        close,
        rsi,
        macd,
        macd_signal,
    ):
        score = 0

        reasons = []

        # =====================================================
        # EMA
        # =====================================================

        if close > ema:

            score += 30

            reasons.append(
                "Price is above EMA"
            )

        else:

            score -= 30

            reasons.append(
                "Price is below EMA"
            )

        # =====================================================
        # RSI
        # =====================================================

        if rsi < 30:

            score += 20

            reasons.append(
                "RSI indicates oversold conditions"
            )

        elif rsi <= 70:

            score += 10

            reasons.append(
                "RSI shows healthy momentum"
            )

        else:

            score -= 20

            reasons.append(
                "RSI indicates overbought conditions"
            )

        # =====================================================
        # MACD
        # =====================================================

        if macd > macd_signal:

            score += 30

            reasons.append(
                "MACD bullish crossover"
            )

        else:

            score -= 30

            reasons.append(
                "MACD bearish crossover"
            )

        # =====================================================
        # FINAL DECISION
        # =====================================================

        if score >= 50:

            signal = "BUY"

        elif score <= -50:

            signal = "SELL"

        else:

            signal = "WAIT"

        confidence = min(
            abs(score),
            100,
        )

        return (
            signal,
            score,
            confidence,
            reasons,
        )

    @staticmethod
    def _create_trade_levels(
        entry_price,
        signal,
    ):

        if signal == "BUY":

            stop_loss = (
                entry_price
                * (
                    1
                    - BacktestEngine.RISK_PERCENT
                )
            )

            target = (
                entry_price
                + (
                    (
                        entry_price
                        - stop_loss
                    )
                    * BacktestEngine.REWARD_MULTIPLIER
                )
            )

        elif signal == "SELL":

            stop_loss = (
                entry_price
                * (
                    1
                    + BacktestEngine.RISK_PERCENT
                )
            )

            target = (
                entry_price
                - (
                    (
                        stop_loss
                        - entry_price
                    )
                    * BacktestEngine.REWARD_MULTIPLIER
                )
            )

        else:

            return None

        return {
            "stop_loss": round(
                stop_loss,
                2,
            ),
            "target": round(
                target,
                2,
            ),
        }

    @staticmethod
    def _check_exit(
        side,
        candle,
        stop_loss,
        target,
    ):

        high = float(
            candle["High"]
        )

        low = float(
            candle["Low"]
        )

        # =====================================================
        # BUY
        # =====================================================

        if side == "BUY":

            stop_hit = (
                low <= stop_loss
            )

            target_hit = (
                high >= target
            )

            # Conservative assumption:
            # If both are touched in the same candle,
            # assume STOP LOSS happened first.

            if stop_hit:

                return (
                    stop_loss,
                    "STOP_LOSS",
                )

            if target_hit:

                return (
                    target,
                    "TARGET",
                )

        # =====================================================
        # SELL
        # =====================================================

        elif side == "SELL":

            stop_hit = (
                high >= stop_loss
            )

            target_hit = (
                low <= target
            )

            # Conservative assumption:
            # Stop loss happens first if both are touched.

            if stop_hit:

                return (
                    stop_loss,
                    "STOP_LOSS",
                )

            if target_hit:

                return (
                    target,
                    "TARGET",
                )

        return None

    @staticmethod
    def _calculate_pnl(
        side,
        entry_price,
        exit_price,
        quantity,
    ):

        if side == "BUY":

            return round(
                (
                    exit_price
                    - entry_price
                )
                * quantity,
                2,
            )

        return round(
            (
                entry_price
                - exit_price
            )
            * quantity,
            2,
        )

    @staticmethod
    def _apply_slippage(
        price,
        side,
        action,
        slippage_percent,
    ):
        """
        Apply adverse execution slippage.

        BUY execution:
            price becomes higher.

        SELL execution:
            price becomes lower.

        The action represents the actual market action:

            BUY  -> pay more
            SELL -> receive less
        """

        del side  # Reserved for future execution modelling.

        slippage_rate = (
            slippage_percent / 100
        )

        if slippage_rate <= 0:

            return float(price)

        if action == "BUY":

            return (
                float(price)
                * (
                    1
                    + slippage_rate
                )
            )

        return (
            float(price)
            * (
                1
                - slippage_rate
            )
        )

    @staticmethod
    def _calculate_transaction_cost(
        entry_price,
        exit_price,
        quantity,
        transaction_cost_percent,
    ):
        """
        Generic turnover-based transaction cost.

        This is intentionally a simplified model
        for Sprint 18.1.

        Later we will introduce separate realistic
        Equity and F&O charge models.
        """

        turnover = (
            abs(
                entry_price
                * quantity
            )
            +
            abs(
                exit_price
                * quantity
            )
        )

        cost = (
            turnover
            * transaction_cost_percent
            / 100
        )

        return round(
            cost,
            2,
        )

    @staticmethod
    def run(
        symbol: str,
        history: pd.DataFrame,
        quantity: int = 1,
        slippage_percent: float = 0.0,
        transaction_cost_percent: float = 0.0,
    ):

        if history is None or history.empty:

            return {
                "error": (
                    "No historical data available."
                )
            }

        if quantity <= 0:

            return {
                "error": (
                    "Quantity must be greater than zero."
                )
            }

        if slippage_percent < 0:

            return {
                "error": (
                    "Slippage percent cannot be negative."
                )
            }

        if transaction_cost_percent < 0:

            return {
                "error": (
                    "Transaction cost percent "
                    "cannot be negative."
                )
            }

        data = history.copy()

        required_columns = {
            "Open",
            "High",
            "Low",
            "Close",
        }

        missing_columns = (
            required_columns
            - set(data.columns)
        )

        if missing_columns:

            return {
                "error": (
                    "Missing required columns: "
                    + ", ".join(
                        sorted(
                            missing_columns
                        )
                    )
                )
            }

        # =====================================================
        # INDICATORS
        # =====================================================

        data["EMA"] = calculate_ema(
            data,
            period=20,
        )

        data["RSI"] = calculate_rsi(
            data,
            period=14,
        )

        (
            data["MACD"],
            data["MACD_SIGNAL"],
            data["MACD_HISTOGRAM"],
        ) = calculate_macd(data)

        # =====================================================
        # REMOVE INVALID INDICATOR ROWS
        # =====================================================

        data = data.dropna(
            subset=[
                "EMA",
                "RSI",
                "MACD",
                "MACD_SIGNAL",
            ]
        ).copy()

        data = data.reset_index()

        trades = []

        trade_id = 1

        i = 0

        while i < len(data) - 1:

            current = data.iloc[i]

            signal_date = (
                current["Date"]
                if "Date" in data.columns
                else current.iloc[0]
            )

            (
                signal,
                score,
                confidence,
                _,
            ) = (
                BacktestEngine
                ._calculate_signal(
                    ema=float(
                        current["EMA"]
                    ),
                    close=float(
                        current["Close"]
                    ),
                    rsi=float(
                        current["RSI"]
                    ),
                    macd=float(
                        current["MACD"]
                    ),
                    macd_signal=float(
                        current["MACD_SIGNAL"]
                    ),
                )
            )

            if signal == "WAIT":

                i += 1
                continue

            # =================================================
            # EXECUTE AT NEXT CANDLE OPEN
            # =================================================

            entry_index = i + 1

            entry_candle = data.iloc[
                entry_index
            ]

            side = signal

            # -------------------------------------------------
            # RAW MARKET ENTRY PRICE
            # -------------------------------------------------
            #
            # This is the actual market Open used by the
            # strategy to establish its theoretical trade.
            #
            # IMPORTANT:
            # SL/Target MUST be calculated from this raw price.
            # Slippage is an execution effect and must not alter
            # the strategy's trade levels or trade count.
            #
            raw_entry_price = float(
                entry_candle["Open"]
            )

            entry_action = (
                "BUY"
                if side == "BUY"
                else "SELL"
            )

            # -------------------------------------------------
            # EXECUTED ENTRY PRICE
            # -------------------------------------------------
            #
            # Slippage is applied only to execution price.
            #
            entry_price = (
                BacktestEngine
                ._apply_slippage(
                    price=raw_entry_price,
                    side=side,
                    action=entry_action,
                    slippage_percent=(
                        slippage_percent
                    ),
                )
            )

            entry_date = (
                entry_candle["Date"]
                if "Date" in data.columns
                else entry_candle.iloc[0]
            )

            # =================================================
            # TRADE LEVELS
            # =================================================
            #
            # IMPORTANT SPRINT 18 FIX:
            #
            # Calculate SL/Target from RAW entry price,
            # NOT slippage-adjusted entry_price.
            #
            # This guarantees:
            #
            # 0% slippage  -> same trade signals
            # 0.1% slippage -> same trade signals
            # 0.5% slippage -> same trade signals
            #
            # Only execution price and P&L change.
            # =================================================

            levels = (
                BacktestEngine
                ._create_trade_levels(
                    raw_entry_price,
                    signal,
                )
            )

            stop_loss = levels[
                "stop_loss"
            ]

            target = levels[
                "target"
            ]

            exit_price = None
            exit_reason = None
            exit_date = None

            # =================================================
            # CHECK ENTRY CANDLE FIRST
            # =================================================

            entry_exit = (
                BacktestEngine
                ._check_exit(
                    side=side,
                    candle=entry_candle,
                    stop_loss=stop_loss,
                    target=target,
                )
            )

            if entry_exit:

                (
                    exit_price,
                    exit_reason,
                ) = entry_exit

                exit_date = entry_date

            else:

                # =============================================
                # CHECK FUTURE CANDLES
                # =============================================

                for j in range(
                    entry_index + 1,
                    len(data),
                ):

                    candle = data.iloc[j]

                    result = (
                        BacktestEngine
                        ._check_exit(
                            side=side,
                            candle=candle,
                            stop_loss=stop_loss,
                            target=target,
                        )
                    )

                    if result:

                        (
                            exit_price,
                            exit_reason,
                        ) = result

                        exit_date = (
                            candle["Date"]
                            if "Date"
                            in data.columns
                            else candle.iloc[0]
                        )

                        break

            # =================================================
            # STILL OPEN AT END OF DATA
            # =================================================

            if exit_price is None:

                final_candle = data.iloc[
                    -1
                ]

                exit_price = float(
                    final_candle["Close"]
                )

                exit_reason = (
                    "END_OF_DATA"
                )

                exit_date = (
                    final_candle["Date"]
                    if "Date"
                    in data.columns
                    else final_candle.iloc[0]
                )

            # =================================================
            # APPLY EXIT SLIPPAGE
            # =================================================

            raw_exit_price = float(
                exit_price
            )

            exit_action = (
                "SELL"
                if side == "BUY"
                else "BUY"
            )

            executed_exit_price = (
                BacktestEngine
                ._apply_slippage(
                    price=raw_exit_price,
                    side=side,
                    action=exit_action,
                    slippage_percent=(
                        slippage_percent
                    ),
                )
            )

            # =================================================
            # GROSS P&L
            # =================================================

            gross_pnl = (
                BacktestEngine
                ._calculate_pnl(
                    side=side,
                    entry_price=entry_price,
                    exit_price=(
                        executed_exit_price
                    ),
                    quantity=quantity,
                )
            )

            # =================================================
            # SLIPPAGE COST
            # =================================================

            entry_slippage_cost = (
                abs(
                    entry_price
                    - raw_entry_price
                )
                * quantity
            )

            exit_slippage_cost = (
                abs(
                    executed_exit_price
                    - raw_exit_price
                )
                * quantity
            )

            slippage_cost = round(
                entry_slippage_cost
                + exit_slippage_cost,
                2,
            )

            # =================================================
            # TRANSACTION COST
            # =================================================

            transaction_cost = (
                BacktestEngine
                ._calculate_transaction_cost(
                    entry_price=entry_price,
                    exit_price=(
                        executed_exit_price
                    ),
                    quantity=quantity,
                    transaction_cost_percent=(
                        transaction_cost_percent
                    ),
                )
            )

            # =================================================
            # NET P&L
            # =================================================

            net_pnl = round(
                gross_pnl
                - transaction_cost,
                2,
            )

            # =================================================
            # CREATE TRADE
            # =================================================

            trades.append(
                BacktestTrade(
                    trade_id=trade_id,

                    symbol=symbol,

                    side=side,

                    signal_date=str(
                        signal_date
                    ),

                    entry_date=str(
                        entry_date
                    ),

                    exit_date=str(
                        exit_date
                    ),

                    entry_price=round(
                        entry_price,
                        2,
                    ),

                    exit_price=round(
                        executed_exit_price,
                        2,
                    ),

                    stop_loss=round(
                        stop_loss,
                        2,
                    ),

                    target=round(
                        target,
                        2,
                    ),

                    gross_pnl=round(
                        gross_pnl,
                        2,
                    ),

                    slippage_cost=round(
                        slippage_cost,
                        2,
                    ),

                    transaction_cost=round(
                        transaction_cost,
                        2,
                    ),

                    net_pnl=round(
                        net_pnl,
                        2,
                    ),

                    # Existing analytics reads pnl.
                    pnl=round(
                        net_pnl,
                        2,
                    ),

                    exit_reason=exit_reason,

                    signal_score=score,

                    confidence=confidence,
                )
            )

            trade_id += 1

            # =================================================
            # MOVE TO AFTER EXIT
            #
            # Prevent overlapping positions.
            # =================================================

            exit_index = entry_index

            if exit_reason != "END_OF_DATA":

                for k in range(
                    entry_index,
                    len(data),
                ):

                    candidate = data.iloc[k]

                    candidate_date = (
                        candidate["Date"]
                        if "Date"
                        in data.columns
                        else candidate.iloc[0]
                    )

                    if str(
                        candidate_date
                    ) == str(
                        exit_date
                    ):

                        exit_index = k

                        break

            else:

                exit_index = (
                    len(data) - 1
                )

            i = exit_index + 1

        return {
            "symbol": symbol,

            "quantity": quantity,

            "slippage_percent": (
                slippage_percent
            ),

            "transaction_cost_percent": (
                transaction_cost_percent
            ),

            "trades": [
                trade.__dict__
                for trade in trades
            ],
        }