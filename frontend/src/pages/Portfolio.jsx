import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function Portfolio() {
  const [portfolio, setPortfolio] = useState(null);
  const [positions, setPositions] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadPortfolio = async (showFullLoader = false) => {
    try {
      if (showFullLoader) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      setError("");

      const [portfolioResponse, positionsResponse] =
        await Promise.all([
          fetch(`${API_URL}/portfolio/`),
          fetch(`${API_URL}/portfolio/positions`),
        ]);

      if (!portfolioResponse.ok) {
        throw new Error("Failed to load portfolio");
      }

      if (!positionsResponse.ok) {
        throw new Error("Failed to load positions");
      }

      const portfolioData = await portfolioResponse.json();
      const positionsData = await positionsResponse.json();

      setPortfolio(portfolioData);
      setPositions(
        Array.isArray(positionsData)
          ? positionsData
          : []
      );
    } catch (err) {
      console.error("Portfolio error:", err);
      setError(
        err.message || "Unable to load portfolio data."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadPortfolio(true);

    const interval = setInterval(() => {
      loadPortfolio(false);
    }, 10000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  const closePosition = async (position) => {
    if (!position.paper_trade_id) {
      window.alert(
        "This position is not linked to a paper trade."
      );
      return;
    }

    const defaultPrice =
      position.current_price ?? position.entry_price;

    const exitPrice = window.prompt(
      `Enter exit price for ${position.symbol}:`,
      defaultPrice
    );

    if (exitPrice === null) {
      return;
    }

    const parsedExitPrice = Number(exitPrice);

    if (
      !Number.isFinite(parsedExitPrice) ||
      parsedExitPrice <= 0
    ) {
      window.alert("Please enter a valid exit price.");
      return;
    }

    const confirmed = window.confirm(
      `Close ${position.symbol} (${position.side} × ${position.quantity}) at ₹${parsedExitPrice.toLocaleString(
        "en-IN",
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }
      )}?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setRefreshing(true);
      setError("");

      const response = await fetch(
        `${API_URL}/paper-trade/${position.paper_trade_id}/close`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            exit_price: parsedExitPrice,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.error ||
            "Failed to close trade."
        );
      }

      await loadPortfolio(false);
    } catch (err) {
      console.error("Close trade error:", err);
      setError(
        err.message || "Unable to close trade."
      );
      setRefreshing(false);
    }
  };

  const formatMoney = (value) => {
    if (value === null || value === undefined) {
      return "—";
    }

    return `₹${Number(value).toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatDate = (value) => {
    if (!value) {
      return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return "—";
    }

    return date.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getSideClass = (side) => {
    const normalized = String(side || "").toUpperCase();

    if (
      normalized === "BUY" ||
      normalized === "LONG"
    ) {
      return "signal-buy";
    }

    if (
      normalized === "SELL" ||
      normalized === "SHORT"
    ) {
      return "signal-sell";
    }

    return "signal-wait";
  };

  const totalUnrealizedPnl = positions.reduce(
    (total, position) =>
      total +
      Number(position.unrealized_pnl || 0),
    0
  );

  return (
    <section className="page-content">

      {/* Header */}
      <div className="page-heading">

        <div>
          <p className="eyebrow">
            PORTFOLIO MANAGEMENT
          </p>

          <h1>
            Portfolio
          </h1>

          <p>
            Track your capital, P&L, positions and trading performance.
          </p>
        </div>

        <button
          className="scan-button"
          onClick={() => loadPortfolio(false)}
          disabled={refreshing}
        >
          {refreshing
            ? "Refreshing..."
            : "↻ Refresh"}
        </button>

      </div>


      {/* Error */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      {/* Main Portfolio Stats */}
      <div className="stats-grid">

        <div className="stat-card">

          <span className="stat-label">
            Trading Capital
          </span>

          <strong>
            {loading
              ? "Loading..."
              : formatMoney(
                  portfolio?.capital
                )}
          </strong>

          <small>
            Starting capital
          </small>

        </div>


        <div className="stat-card">

          <span className="stat-label">
            Current Balance
          </span>

          <strong>
            {loading
              ? "Loading..."
              : formatMoney(
                  portfolio?.current_balance
                )}
          </strong>

          <small
            className={
              Number(
                portfolio?.net_pnl || 0
              ) >= 0
                ? "positive"
                : "negative"
            }
          >
            {loading
              ? ""
              : `${
                  Number(
                    portfolio?.net_pnl || 0
                  ) >= 0
                    ? "+"
                    : ""
                }${formatMoney(
                  portfolio?.net_pnl
                )}`}
          </small>

        </div>


        <div className="stat-card">

          <span className="stat-label">
            Unrealized P&L
          </span>

          <strong>
            {formatMoney(
              totalUnrealizedPnl
            )}
          </strong>

          <small
            className={
              totalUnrealizedPnl >= 0
                ? "positive"
                : "negative"
            }
          >
            Open positions
          </small>

        </div>


        <div className="stat-card">

          <span className="stat-label">
            Win Rate
          </span>

          <strong>
            {loading
              ? "Loading..."
              : `${portfolio?.win_rate ?? 0}%`}
          </strong>

          <small>
            {portfolio?.winning_trades ?? 0} winning trades
          </small>

        </div>

      </div>


      {/* Secondary Stats */}
      <div className="stats-grid portfolio-secondary-stats">

        <div className="stat-card">

          <span className="stat-label">
            Total Trades
          </span>

          <strong>
            {portfolio?.total_trades ?? 0}
          </strong>

          <small>
            All recorded trades
          </small>

        </div>


        <div className="stat-card">

          <span className="stat-label">
            Open Trades
          </span>

          <strong>
            {portfolio?.open_trades ?? 0}
          </strong>

          <small>
            Currently active
          </small>

        </div>


        <div className="stat-card">

          <span className="stat-label">
            Closed Trades
          </span>

          <strong>
            {portfolio?.closed_trades ?? 0}
          </strong>

          <small>
            Completed trades
          </small>

        </div>


        <div className="stat-card">

          <span className="stat-label">
            Total Profit
          </span>

          <strong>
            {formatMoney(
              portfolio?.total_profit
            )}
          </strong>

          <small className="positive">
            Realized winning trades
          </small>

        </div>

      </div>


      {/* Open Positions */}
      <div className="panel positions-panel">

        <div className="panel-header">

          <div>
            <span className="panel-label">
              ACTIVE POSITIONS
            </span>

            <h2>
              Open Positions
            </h2>
          </div>

          <span className="live-badge">
            {positions.length} OPEN
          </span>

        </div>


        {positions.length === 0 ? (

          <div className="empty-state">

            <p>
              No open positions.
            </p>

            <small>
              Positions will appear here when paper trades are opened.
            </small>

          </div>

        ) : (

          <div className="positions-table">

            <div className="position-row position-head">

              <span>
                Symbol
              </span>

              <span>
                Side
              </span>

              <span>
                Qty
              </span>

              <span>
                Entry
              </span>

              <span>
                Current
              </span>

              <span>
                Stop Loss
              </span>

              <span>
                Target
              </span>

              <span>
                Unrealized P&L
              </span>

              <span>
                Updated
              </span>

              <span>
                Action
              </span>

            </div>


            {positions.map((position) => (

              <div
                className="position-row"
                key={position.id}
              >

                <strong>
                  {position.symbol}
                </strong>


                <span
                  className={getSideClass(
                    position.side
                  )}
                >
                  {String(
                    position.side || ""
                  ).toUpperCase()}
                </span>


                <span>
                  {position.quantity}
                </span>


                <span>
                  {formatMoney(
                    position.entry_price
                  )}
                </span>


                <span>
                  {formatMoney(
                    position.current_price
                  )}
                </span>


                <span>
                  {formatMoney(
                    position.stop_loss
                  )}
                </span>


                <span>
                  {formatMoney(
                    position.target
                  )}
                </span>


                <span
                  className={
                    Number(
                      position.unrealized_pnl || 0
                    ) >= 0
                      ? "positive"
                      : "negative"
                  }
                >
                  {Number(
                    position.unrealized_pnl || 0
                  ) >= 0
                    ? "+"
                    : ""}

                  {formatMoney(
                    position.unrealized_pnl
                  )}
                </span>


                <span>
                  {formatDate(
                    position.updated_at
                  )}
                </span>


                <button
                  className="close-position-button"
                  onClick={() =>
                    closePosition(position)
                  }
                  disabled={refreshing}
                >
                  Close
                </button>

              </div>

            ))}

          </div>

        )}

      </div>

    </section>
  );
}

export default Portfolio;