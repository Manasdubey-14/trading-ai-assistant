import { useCallback, useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function PaperTrading() {
  const [trades, setTrades] = useState([]);
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [selectedTradeId, setSelectedTradeId] = useState(null);

  const emptyFilters = {
    status: "ALL",
    symbol: "",
    strategy: "",
    fromDate: "",
    toDate: "",
  };

  const [filters, setFilters] = useState(emptyFilters);
  const [appliedFilters, setAppliedFilters] = useState(emptyFilters);

  const [form, setForm] = useState({
    symbol: "",
    trade_type: "BUY",
    quantity: 1,
    stop_loss: "",
    target: "",
    strategy: "",
    timeframe: "1D",
    confidence: "",
    notes: "",
  });

  const loadTrades = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const params = new URLSearchParams({ limit: "100" });

      if (appliedFilters.status !== "ALL") {
        params.set("status", appliedFilters.status);
      }

      if (appliedFilters.symbol.trim()) {
        params.set(
          "symbol",
          appliedFilters.symbol.trim().toUpperCase()
        );
      }

      if (appliedFilters.strategy.trim()) {
        params.set("strategy", appliedFilters.strategy.trim());
      }

      if (appliedFilters.fromDate) {
        params.set(
          "from_date",
          `${appliedFilters.fromDate}T00:00:00`
        );
      }

      if (appliedFilters.toDate) {
        params.set(
          "to_date",
          `${appliedFilters.toDate}T23:59:59.999`
        );
      }

      const [response, positionsResponse] = await Promise.all([
        fetch(`${API_URL}/paper-trade/?${params.toString()}`),
        fetch(`${API_URL}/portfolio/positions`),
      ]);

      if (!response.ok) {
        throw new Error("Failed to load paper trades");
      }

      const data = await response.json();

      setTrades(Array.isArray(data) ? data : []);

      if (positionsResponse.ok) {
        const positionData = await positionsResponse.json();
        setPositions(Array.isArray(positionData) ? positionData : []);
      } else {
        setPositions([]);
      }
    } catch (err) {
      console.error("Paper trading error:", err);
      setError(
        err.message || "Unable to load paper trades."
      );
    } finally {
      setLoading(false);
    }
  }, [appliedFilters]);

  useEffect(() => {
    loadTrades();

    const interval = setInterval(() => {
      loadTrades();
    }, 10000);

    return () => {
      clearInterval(interval);
    };
  }, [loadTrades]);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;

    setFilters((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const applyFilters = (event) => {
    event.preventDefault();
    setAppliedFilters({ ...filters });
  };

  const clearFilters = () => {
    setFilters(emptyFilters);
    setAppliedFilters(emptyFilters);
  };

  const createTrade = async (event) => {
    event.preventDefault();

    try {
      setSubmitting(true);
      setError("");

      const payload = {
        symbol: form.symbol.trim().toUpperCase(),
        trade_type: form.trade_type,
        quantity: Number(form.quantity),
        stop_loss: Number(form.stop_loss),
        target: Number(form.target),
        strategy: form.strategy || null,
        timeframe: form.timeframe || null,
        confidence:
          form.confidence === ""
            ? null
            : Number(form.confidence),
        notes: form.notes || null,
      };

      if (
        !payload.symbol ||
        !Number.isFinite(payload.quantity) ||
        payload.quantity <= 0 ||
        !Number.isFinite(payload.stop_loss) ||
        payload.stop_loss <= 0 ||
        !Number.isFinite(payload.target) ||
        payload.target <= 0
      ) {
        throw new Error(
          "Please provide valid trade details."
        );
      }

      const response = await fetch(
        `${API_URL}/paper-trade/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.error ||
            "Failed to create paper trade."
        );
      }

      setForm({
        symbol: "",
        trade_type: "BUY",
        quantity: 1,
        stop_loss: "",
        target: "",
        strategy: "",
        timeframe: "1D",
        confidence: "",
        notes: "",
      });

      await loadTrades();
    } catch (err) {
      console.error("Create trade error:", err);
      setError(
        err.message || "Unable to create paper trade."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const closeTrade = async (trade) => {
    const exitPrice = window.prompt(
      `Enter exit price for ${trade.symbol}:`,
      trade.entry_price
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
      `Close ${trade.symbol} ${trade.trade_type} × ${trade.quantity} at ₹${parsedExitPrice.toLocaleString(
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
      setSubmitting(true);
      setError("");

      const response = await fetch(
        `${API_URL}/paper-trade/${trade.id}/close`,
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

      await loadTrades();
    } catch (err) {
      console.error("Close trade error:", err);
      setError(
        err.message || "Unable to close trade."
      );
    } finally {
      setSubmitting(false);
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

  const openTrades = trades.filter(
    (trade) => trade.status === "OPEN"
  );

  const closedTrades = trades.filter(
    (trade) => trade.status === "CLOSED"
  );

  const realizedPnl = closedTrades.reduce(
    (total, trade) =>
      total + Number(trade.pnl || 0),
    0
  );

  const totalProfit = closedTrades
    .filter((trade) => Number(trade.pnl || 0) > 0)
    .reduce(
      (total, trade) =>
        total + Number(trade.pnl || 0),
      0
    );

  const totalLoss = closedTrades
    .filter((trade) => Number(trade.pnl || 0) < 0)
    .reduce(
      (total, trade) =>
        total + Number(trade.pnl || 0),
      0
    );

  const selectedTrade = trades.find(
    (trade) => trade.id === selectedTradeId
  );

  const selectedPosition = positions.find(
    (position) => position.paper_trade_id === selectedTradeId
  );

  const getTradeMetrics = (trade) => {
    const entryPrice = Number(trade.entry_price || 0);
    const stopLoss = Number(trade.stop_loss || 0);
    const target = Number(trade.target || 0);
    const quantity = Number(trade.quantity || 0);
    const riskPerShare = Math.abs(entryPrice - stopLoss);
    const rewardPerShare = Math.abs(target - entryPrice);
    const riskAmount = riskPerShare * quantity;
    const plannedRiskReward = riskPerShare
      ? rewardPerShare / riskPerShare
      : null;
    const actualRiskMultiple = trade.status === "CLOSED" && riskAmount
      ? Number(trade.pnl || 0) / riskAmount
      : null;

    return {
      riskAmount,
      plannedRiskReward,
      actualRiskMultiple,
    };
  };

  const getHoldingDuration = (trade) => {
    if (!trade?.created_at) return "—";

    const start = new Date(trade.created_at);
    const end = trade.closed_at ? new Date(trade.closed_at) : new Date();
    const elapsedMinutes = Math.max(
      0,
      Math.floor((end.getTime() - start.getTime()) / 60000)
    );
    const days = Math.floor(elapsedMinutes / 1440);
    const hours = Math.floor((elapsedMinutes % 1440) / 60);
    const minutes = elapsedMinutes % 60;

    if (days) return `${days}d ${hours}h`;
    if (hours) return `${hours}h ${minutes}m`;

    return `${minutes}m`;
  };

  return (
    <section className="page-content">

      {/* Header */}
      <div className="page-heading">

        <div>
          <p className="eyebrow">
            SIMULATED TRADING
          </p>

          <h1>
            Paper Trading
          </h1>

          <p>
            Practice trades using real market prices without risking real capital.
          </p>
        </div>

        <button
          className="scan-button"
          onClick={loadTrades}
          disabled={loading || submitting}
        >
          {loading ? "Loading..." : "↻ Refresh"}
        </button>

      </div>


      {/* Error */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      {/* Summary */}
      <div className="stats-grid">

        <div className="stat-card">
          <span className="stat-label">
            Total Trades
          </span>

          <strong>
            {trades.length}
          </strong>

          <small>
            Recorded paper trades
          </small>
        </div>


        <div className="stat-card">
          <span className="stat-label">
            Open Trades
          </span>

          <strong>
            {openTrades.length}
          </strong>

          <small>
            Currently active
          </small>
        </div>


        <div className="stat-card">
          <span className="stat-label">
            Realized P&L
          </span>

          <strong>
            {formatMoney(realizedPnl)}
          </strong>

          <small
            className={
              realizedPnl >= 0
                ? "positive"
                : "negative"
            }
          >
            Closed trades
          </small>
        </div>


        <div className="stat-card">
          <span className="stat-label">
            Profit / Loss
          </span>

          <strong>
            {formatMoney(totalProfit)}
          </strong>

          <small
            className={
              totalLoss < 0
                ? "negative"
                : "positive"
            }
          >
            Loss: {formatMoney(totalLoss)}
          </small>
        </div>

      </div>


      <div className="panel journal-filters-panel">
        <div className="panel-header">
          <div>
            <span className="panel-label">TRADE JOURNAL</span>
            <h2>Filter Trade History</h2>
          </div>

          <span className="journal-filter-count">
            {trades.length} matching record{trades.length === 1 ? "" : "s"}
          </span>
        </div>

        <form className="journal-filters" onSubmit={applyFilters}>
          <div className="form-field">
            <label>Status</label>
            <select
              name="status"
              value={filters.status}
              onChange={handleFilterChange}
            >
              <option value="ALL">All statuses</option>
              <option value="OPEN">Open</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>

          <div className="form-field">
            <label>Symbol</label>
            <input
              name="symbol"
              value={filters.symbol}
              onChange={handleFilterChange}
              placeholder="RELIANCE.NS"
            />
          </div>

          <div className="form-field">
            <label>Strategy</label>
            <input
              name="strategy"
              value={filters.strategy}
              onChange={handleFilterChange}
              placeholder="Exact strategy name"
            />
          </div>

          <div className="form-field">
            <label>Opened from</label>
            <input
              name="fromDate"
              type="date"
              value={filters.fromDate}
              onChange={handleFilterChange}
            />
          </div>

          <div className="form-field">
            <label>Opened to</label>
            <input
              name="toDate"
              type="date"
              value={filters.toDate}
              onChange={handleFilterChange}
            />
          </div>

          <div className="journal-filter-actions">
            <button type="submit" className="scan-button" disabled={loading}>
              Apply Filters
            </button>
            <button type="button" className="journal-clear-button" onClick={clearFilters}>
              Clear
            </button>
          </div>
        </form>
      </div>


      {/* Create trade */}
      <div className="panel paper-trade-form-panel">

        <div className="panel-header">

          <div>
            <span className="panel-label">
              NEW PAPER TRADE
            </span>

            <h2>
              Create Trade
            </h2>
          </div>

          <span className="live-badge">
            PAPER
          </span>

        </div>


        <form
          className="paper-trade-form"
          onSubmit={createTrade}
        >

          <div className="form-field">
            <label>
              Symbol
            </label>

            <input
              name="symbol"
              value={form.symbol}
              onChange={handleChange}
              placeholder="RELIANCE.NS"
              required
            />
          </div>


          <div className="form-field">
            <label>
              Side
            </label>

            <select
              name="trade_type"
              value={form.trade_type}
              onChange={handleChange}
            >
              <option value="BUY">
                BUY
              </option>

              <option value="SELL">
                SELL
              </option>
            </select>
          </div>


          <div className="form-field">
            <label>
              Quantity
            </label>

            <input
              name="quantity"
              type="number"
              min="1"
              value={form.quantity}
              onChange={handleChange}
              required
            />
          </div>


          <div className="form-field">
            <label>
              Entry Price
            </label>

            <div className="auto-price-field">
              <strong>
                Market Price
              </strong>

              <small>
                Automatically fetched by backend
              </small>
            </div>
          </div>


          <div className="form-field">
            <label>
              Stop Loss
            </label>

            <input
              name="stop_loss"
              type="number"
              step="0.01"
              min="0"
              value={form.stop_loss}
              onChange={handleChange}
              placeholder="1280.00"
              required
            />
          </div>


          <div className="form-field">
            <label>
              Target
            </label>

            <input
              name="target"
              type="number"
              step="0.01"
              min="0"
              value={form.target}
              onChange={handleChange}
              placeholder="1340.00"
              required
            />
          </div>


          <div className="form-field">
            <label>
              Strategy
            </label>

            <input
              name="strategy"
              value={form.strategy}
              onChange={handleChange}
              placeholder="EMA + RSI + MACD"
            />
          </div>


          <div className="form-field">
            <label>
              Timeframe
            </label>

            <select
              name="timeframe"
              value={form.timeframe}
              onChange={handleChange}
            >
              <option value="5m">5m</option>
              <option value="15m">15m</option>
              <option value="1H">1H</option>
              <option value="1D">1D</option>
            </select>
          </div>


          <div className="form-field">
            <label>
              Confidence
            </label>

            <input
              name="confidence"
              type="number"
              step="0.01"
              min="0"
              max="100"
              value={form.confidence}
              onChange={handleChange}
              placeholder="70"
            />
          </div>


          <div className="form-field form-field-wide">
            <label>
              Notes
            </label>

            <input
              name="notes"
              value={form.notes}
              onChange={handleChange}
              placeholder="Reason for taking the trade"
            />
          </div>


          <div className="form-actions">
            <button
              type="submit"
              className="scan-button"
              disabled={submitting}
            >
              {submitting
                ? "Processing..."
                : "Create Paper Trade"}
            </button>
          </div>

        </form>

      </div>


      {/* Trade history */}
      <div className="panel paper-trades-panel">

        <div className="panel-header">

          <div>
            <span className="panel-label">
              TRADE JOURNAL
            </span>

            <h2>
              Paper Trade Ledger
            </h2>
          </div>

          <span className="live-badge">
            {openTrades.length} OPEN
          </span>

        </div>


        {trades.length === 0 ? (

          <div className="empty-state">

            <p>
              No paper trades yet.
            </p>

            <small>
              Create your first simulated trade above.
            </small>

          </div>

        ) : (

          <div className="paper-trades-table">

            <div className="paper-trade-row paper-trade-head">
              <span>ID</span>
              <span>Symbol</span>
              <span>Side</span>
              <span>Qty</span>
              <span>Entry</span>
              <span>Exit</span>
              <span>Stop Loss</span>
              <span>Target</span>
              <span>P&L</span>
              <span>Status</span>
              <span>Exit Reason</span>
              <span>Action</span>
            </div>


            {trades.map((trade) => (

              <div
                className="paper-trade-row"
                key={trade.id}
              >

                <span>
                  #{trade.id}
                </span>

                <strong>
                  {trade.symbol}
                </strong>

                <span
                  className={
                    trade.trade_type === "BUY"
                      ? "signal-buy"
                      : "signal-sell"
                  }
                >
                  {trade.trade_type}
                </span>

                <span>
                  {trade.quantity}
                </span>

                <span>
                  {formatMoney(
                    trade.entry_price
                  )}
                </span>

                <span>
                  {formatMoney(
                    trade.exit_price
                  )}
                </span>

                <span>
                  {formatMoney(
                    trade.stop_loss
                  )}
                </span>

                <span>
                  {formatMoney(
                    trade.target
                  )}
                </span>

                <span
                  className={
                    Number(trade.pnl || 0) >= 0
                      ? "positive"
                      : "negative"
                  }
                >
                  {Number(trade.pnl || 0) >= 0
                    ? "+"
                    : ""}
                  {formatMoney(trade.pnl)}
                </span>

                <span>
                  <span
                    className={
                      trade.status === "OPEN"
                        ? "trade-status-open"
                        : "trade-status-closed"
                    }
                  >
                    {trade.status}
                  </span>
                </span>

                <span>
                  {trade.exit_reason || "—"}
                </span>

                <div className="journal-row-actions">
                  <button
                    className="journal-view-button"
                    onClick={() => setSelectedTradeId(trade.id)}
                  >
                    View
                  </button>

                  {trade.status === "OPEN" && (
                    <button
                      className="close-position-button"
                      onClick={() =>
                        closeTrade(trade)
                      }
                      disabled={submitting}
                    >
                      Close
                    </button>
                  )}
                </div>

              </div>

            ))}

          </div>

        )}

      </div>


      {selectedTrade && (() => {
        const metrics = getTradeMetrics(selectedTrade);

        return (
          <section className="panel journal-detail-panel">
            <div className="panel-header">
              <div>
                <span className="panel-label">TRADE REVIEW</span>
                <h2>
                  #{selectedTrade.id} · {selectedTrade.symbol}
                </h2>
              </div>

              <button
                className="journal-clear-button"
                onClick={() => setSelectedTradeId(null)}
              >
                Close Details
              </button>
            </div>

            <div className="journal-detail-grid">
              <div className="journal-detail-section">
                <span className="panel-label">SETUP</span>
                <div className="journal-detail-values">
                  <div><span>Strategy</span><strong>{selectedTrade.strategy || "—"}</strong></div>
                  <div><span>Timeframe</span><strong>{selectedTrade.timeframe || "—"}</strong></div>
                  <div><span>Confidence</span><strong>{selectedTrade.confidence == null ? "—" : `${selectedTrade.confidence}%`}</strong></div>
                  <div><span>Side</span><strong>{selectedTrade.trade_type}</strong></div>
                </div>
              </div>

              <div className="journal-detail-section">
                <span className="panel-label">PLAN VS OUTCOME</span>
                <div className="journal-detail-values">
                  <div><span>Planned risk</span><strong>{formatMoney(metrics.riskAmount)}</strong></div>
                  <div><span>Planned R:R</span><strong>{metrics.plannedRiskReward == null ? "—" : metrics.plannedRiskReward.toFixed(2)}</strong></div>
                  <div><span>Actual R</span><strong>{metrics.actualRiskMultiple == null ? "—" : metrics.actualRiskMultiple.toFixed(2)}</strong></div>
                  <div><span>Holding duration</span><strong>{getHoldingDuration(selectedTrade)}</strong></div>
                </div>
              </div>

              <div className="journal-detail-section">
                <span className="panel-label">EXECUTION</span>
                <div className="journal-detail-values">
                  <div><span>Opened</span><strong>{formatDate(selectedTrade.created_at)}</strong></div>
                  <div><span>Closed</span><strong>{formatDate(selectedTrade.closed_at)}</strong></div>
                  <div><span>Exit reason</span><strong>{selectedTrade.exit_reason || "Monitoring"}</strong></div>
                  <div><span>Outcome</span><strong className={Number(selectedTrade.pnl || 0) >= 0 ? "positive" : "negative"}>{selectedTrade.status === "CLOSED" ? formatMoney(selectedTrade.pnl) : "Open trade"}</strong></div>
                </div>
              </div>

              <div className="journal-detail-section journal-notes-section">
                <span className="panel-label">TRADE NOTES</span>
                <p>{selectedTrade.notes || "No trade notes were recorded."}</p>
              </div>

              {selectedPosition && (
                <div className="journal-detail-section journal-live-section">
                  <span className="panel-label">LIVE POSITION</span>
                  <div className="journal-detail-values">
                    <div><span>Current price</span><strong>{formatMoney(selectedPosition.current_price)}</strong></div>
                    <div><span>Unrealized P&amp;L</span><strong className={Number(selectedPosition.unrealized_pnl || 0) >= 0 ? "positive" : "negative"}>{formatMoney(selectedPosition.unrealized_pnl)}</strong></div>
                    <div><span>Last updated</span><strong>{formatDate(selectedPosition.updated_at)}</strong></div>
                  </div>
                </div>
              )}
            </div>
          </section>
        );
      })()}


      <div className="paper-trading-note">
        <strong>
          Paper Trading Mode
        </strong>

        <span>
          Entry price is fetched automatically from the market-data service. No real broker order is placed.
        </span>
      </div>

    </section>
  );
}

export default PaperTrading;
