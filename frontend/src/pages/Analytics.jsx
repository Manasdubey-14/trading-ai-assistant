import { useEffect, useMemo, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function formatMoney(value) {
  const amount = Number(value || 0);

  return `₹${amount.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function formatPnl(value) {
  const amount = Number(value || 0);
  const prefix = amount > 0 ? "+" : "";

  return `${prefix}${formatMoney(amount)}`;
}

function getPnlClass(value) {
  if (Number(value || 0) > 0) return "positive";
  if (Number(value || 0) < 0) return "negative";
  return "neutral-value";
}

function formatDate(value) {
  if (!value) return "—";

  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
  }).format(new Date(value));
}

function CumulativePnlChart({ points }) {
  const chart = useMemo(() => {
    if (!points?.length) return null;

    const width = 720;
    const height = 250;
    const padding = {
      top: 20,
      right: 20,
      bottom: 32,
      left: 54,
    };

    const values = [0, ...points.map((point) => Number(point.cumulative_pnl || 0))];
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const valueRange = maxValue - minValue || 1;
    const plotWidth = width - padding.left - padding.right;
    const plotHeight = height - padding.top - padding.bottom;

    const getX = (index) => {
      if (points.length === 1) return padding.left + plotWidth / 2;

      return padding.left + (index / (points.length - 1)) * plotWidth;
    };

    const getY = (value) => (
      padding.top + ((maxValue - value) / valueRange) * plotHeight
    );

    const linePoints = points
      .map((point, index) => (
        `${getX(index)},${getY(Number(point.cumulative_pnl || 0))}`
      ))
      .join(" ");

    return {
      width,
      height,
      padding,
      linePoints,
      zeroY: getY(0),
      lastPoint: points[points.length - 1],
      firstDate: formatDate(points[0].closed_at),
      lastDate: formatDate(points[points.length - 1].closed_at),
      yLabels: [maxValue, (maxValue + minValue) / 2, minValue],
      getY,
    };
  }, [points]);

  if (!chart) {
    return (
      <div className="analytics-chart-empty">
        No closed-trade history yet.
      </div>
    );
  }

  return (
    <div className="analytics-chart-wrap">
      <svg
        className="analytics-chart"
        viewBox={`0 0 ${chart.width} ${chart.height}`}
        role="img"
        aria-label="Cumulative profit and loss chart"
      >
        {chart.yLabels.map((value, index) => {
          const y = chart.getY(value);

          return (
            <g key={`${value}-${index}`}>
              <line
                className="analytics-grid-line"
                x1={chart.padding.left}
                x2={chart.width - chart.padding.right}
                y1={y}
                y2={y}
              />
              <text className="analytics-axis-label" x="0" y={y + 4}>
                {formatMoney(value)}
              </text>
            </g>
          );
        })}

        <line
          className="analytics-zero-line"
          x1={chart.padding.left}
          x2={chart.width - chart.padding.right}
          y1={chart.zeroY}
          y2={chart.zeroY}
        />

        <polyline
          className={getPnlClass(chart.lastPoint.cumulative_pnl) === "negative"
            ? "analytics-line analytics-line-negative"
            : "analytics-line"}
          points={chart.linePoints}
        />
      </svg>

      <div className="analytics-chart-dates">
        <span>{chart.firstDate}</span>
        <span>{chart.lastDate}</span>
      </div>
    </div>
  );
}
function BreakdownCard({ title, label, data }) {
  const entries = Object.entries(data || {});

  return (
    <div className="panel analytics-breakdown-card analytics-performance-breakdown">
      <div className="panel-header">
        <div>
          <span className="panel-label">PERFORMANCE BREAKDOWN</span>
          <h2>{title}</h2>
        </div>
      </div>

      {entries.length === 0 ? (
        <div className="analytics-breakdown-empty">
          No closed-trade data yet.
        </div>
      ) : (
        <div className="analytics-table-wrap">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>{label}</th>
                <th>Trades</th>
                <th>Win Rate</th>
                <th>P&L</th>
                <th>Profit Factor</th>
                <th>Avg Win</th>
                <th>Avg Loss</th>
                <th>Target</th>
                <th>SL</th>
                <th>Manual</th>
              </tr>
            </thead>

            <tbody>
              {entries.map(([name, item]) => (
                <tr key={name}>
                  <td>
                    <strong>{name}</strong>
                  </td>

                  <td>
                    {item.trades}
                  </td>

                  <td>
                    {Number(
                      item.win_rate || 0
                    ).toFixed(1)}
                    %
                  </td>

                  <td
                    className={getPnlClass(
                      item.total_pnl
                    )}
                  >
                    {formatPnl(
                      item.total_pnl
                    )}
                  </td>

                  <td>
                    {Number(
                      item.profit_factor || 0
                    ).toFixed(2)}
                  </td>

                  <td
                    className="positive"
                  >
                    {formatMoney(
                      item.average_win
                    )}
                  </td>

                  <td
                    className="negative"
                  >
                    {formatMoney(
                      item.average_loss
                    )}
                  </td>

                  <td>
                    {item.target_hits || 0}
                  </td>

                  <td>
                    {item.stop_loss_hits || 0}
                  </td>

                  <td>
                    {item.manual_exits || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <span className="analytics-breakdown-footnote">
        Grouped by {label}
      </span>
    </div>
  );
}

function Analytics() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadAnalytics = async ({ isRefresh = false } = {}) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const response = await fetch(`${API_URL}/analytics/summary`);

      if (!response.ok) {
        throw new Error("Failed to load analytics summary");
      }

      setSummary(await response.json());
    } catch (err) {
      console.error("Analytics error:", err);
      setError("Unable to load trading analytics.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  const currentStreak = summary?.current_streak
    ? `${summary.current_streak} ${String(summary.current_streak_type || "").toLowerCase()}${summary.current_streak === 1 ? "" : "s"}`
    : "No active streak";

  return (
    <section className="page-content analytics-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">PERFORMANCE INTELLIGENCE</p>
          <h1>Analytics</h1>
          <p>
            Review closed paper trades, performance trends, and strategy outcomes.
          </p>
        </div>

        <button
          className="scan-button"
          onClick={() => loadAnalytics({ isRefresh: true })}
          disabled={loading || refreshing}
        >
          {refreshing ? "Refreshing..." : "↻ Refresh"}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="panel analytics-loading-state">
          <p>Loading trading analytics...</p>
        </div>
      ) : summary && (
        <>
          <div className="analytics-summary">
            <div className="stat-card">
              <span className="stat-label">Net P&amp;L</span>
              <strong className={getPnlClass(summary.total_pnl)}>
                {formatPnl(summary.total_pnl)}
              </strong>
              <small>
                {formatMoney(summary.gross_profit)} gross profit · {formatMoney(summary.gross_loss)} gross loss
              </small>
            </div>

            <div className="stat-card">
              <span className="stat-label">Win Rate</span>
              <strong>{Number(summary.win_rate || 0).toFixed(1)}%</strong>
              <small>
                {summary.winning_trades} wins · {summary.losing_trades} losses
              </small>
            </div>

            <div className="stat-card">
              <span className="stat-label">Profit Factor</span>
              <strong>{Number(summary.profit_factor || 0).toFixed(2)}</strong>
              <small>Gross profit ÷ gross loss</small>
            </div>

            <div className="stat-card">
              <span className="stat-label">Maximum Drawdown</span>
              <strong className="negative">{formatMoney(summary.maximum_drawdown)}</strong>
              <small>{Number(summary.maximum_drawdown_percent || 0).toFixed(2)}% from peak</small>
            </div>
          </div>

          {summary.total_trades === 0 && (
            <div className="panel analytics-empty-state">
              <p>No closed paper trades yet.</p>
              <small>Close paper trades to begin tracking performance and strategy results.</small>
            </div>
          )}

          <div className="analytics-main-grid">
            <div className="panel analytics-performance-panel">
              <div className="panel-header">
                <div>
                  <span className="panel-label">EQUITY CURVE</span>
                  <h2>Cumulative P&amp;L</h2>
                </div>

                <span className="live-badge">
                  {summary.total_trades} CLOSED
                </span>
              </div>

              <CumulativePnlChart points={summary.cumulative_pnl} />
            </div>

            <div className="panel analytics-trade-quality-panel">
              <div className="panel-header">
                <div>
                  <span className="panel-label">TRADE QUALITY</span>
                  <h2>Performance Details</h2>
                </div>
              </div>

              <div className="analytics-detail-list">
                <div>
                  <span>Average win</span>
                  <strong className="positive">{formatMoney(summary.average_win)}</strong>
                </div>
                <div>
                  <span>Average loss</span>
                  <strong className="negative">{formatMoney(summary.average_loss)}</strong>
                </div>
                <div>
                  <span>Best trade</span>
                  <strong className={getPnlClass(summary.best_trade)}>{formatPnl(summary.best_trade)}</strong>
                </div>
                <div>
                  <span>Worst trade</span>
                  <strong className={getPnlClass(summary.worst_trade)}>{formatPnl(summary.worst_trade)}</strong>
                </div>
              </div>

              <div className="analytics-streak">
                <div>
                  <span className="panel-label">CURRENT STREAK</span>
                  <strong>{currentStreak}</strong>
                </div>
                <div>
                  <span>Best: {summary.best_winning_streak} wins</span>
                  <span>Worst: {summary.worst_losing_streak} losses</span>
                </div>
              </div>
            </div>
          </div>

          <div className="analytics-breakdowns">
            <BreakdownCard
              title="Exit Reasons"
              label="exit reason"
              data={summary.exit_reason_breakdown}
            />
            <BreakdownCard
              title="Strategies"
              label="strategy"
              data={summary.strategy_breakdown}
            />
            <BreakdownCard
              title="Timeframes"
              label="timeframe"
              data={summary.timeframe_breakdown}
            />
          </div>
        </>
      )}
    </section>
  );
}

export default Analytics;
