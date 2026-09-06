import { useEffect, useState } from "react";
import Scanner from "./pages/Scanner";
import Markets from "./pages/Markets";
import Opportunities from "./pages/Opportunities";
import Portfolio from "./pages/Portfolio";
import PaperTrading from "./pages/PaperTrading";
import Analytics from "./pages/Analytics";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [activePage, setActivePage] = useState("dashboard");

  const [capital, setCapital] = useState(0);
  const [currentBalance, setCurrentBalance] = useState(0);
  const [winRate, setWinRate] = useState(0);
  const [openTrades, setOpenTrades] = useState(0);
  const [totalTrades, setTotalTrades] = useState(0);

  const [signals, setSignals] = useState([]);
  const [opportunities, setOpportunities] = useState([]);

  const [loading, setLoading] = useState(true);
  const [scannerLoading, setScannerLoading] = useState(false);
  const [error, setError] = useState("");

  // -----------------------------------------
  // LOAD DASHBOARD DATA
  // -----------------------------------------

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/dashboard/`);

      if (!response.ok) {
        throw new Error("Failed to fetch dashboard data");
      }

      const data = await response.json();

      console.log("Dashboard:", data);

      if (data.portfolio) {
        setCapital(data.portfolio.capital ?? 0);
        setCurrentBalance(data.portfolio.current_balance ?? 0);
        setWinRate(data.portfolio.win_rate ?? 0);
        setOpenTrades(data.portfolio.open_trades ?? 0);
        setTotalTrades(data.portfolio.total_trades ?? 0);
      }

      setSignals(data.latest_signals ?? []);
      setOpportunities(data.top_opportunities ?? []);
    } catch (err) {
      console.error("Dashboard error:", err);
      setError("Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------------------
  // SCAN MARKET
  // -----------------------------------------

  const scanMarket = async () => {
    try {
      setScannerLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/scanner/`);

      if (!response.ok) {
        throw new Error("Market scanner failed");
      }

      const data = await response.json();

      console.log("Scanner results:", data);

      setOpportunities(data);
      setSignals(data.slice(0, 5));
    } catch (err) {
      console.error("Scanner error:", err);
      setError("Market scan failed. Check the backend.");
    } finally {
      setScannerLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  // -----------------------------------------
  // HELPERS
  // -----------------------------------------

  const formatMoney = (value) => {
    return `₹${Number(value || 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    })}`;
  };

  const formatConfidence = (value) => {
    return `${Number(value || 0)}%`;
  };

  const getSignalClass = (signal) => {
    if (signal === "BUY") return "signal-buy";
    if (signal === "SELL") return "signal-sell";
    return "signal-wait";
  };

  // -----------------------------------------
  // RENDER
  // -----------------------------------------

  return (
    <div className="app">

      {/* =========================================
          SIDEBAR
      ========================================= */}

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">AI</div>

          <div>
            <strong>TradeAI</strong>
            <small>Trading Assistant</small>
          </div>
        </div>

        <nav className="navigation">

          <p className="nav-title">MAIN</p>

          <button
            className={`nav-item ${
              activePage === "dashboard" ? "active" : ""
            }`}
            onClick={() => setActivePage("dashboard")}
          >
            <span>▦</span>
            Dashboard
          </button>

          <button
            className={`nav-item ${
              activePage === "markets" ? "active" : ""
            }`}
            onClick={() => setActivePage("markets")}
          >
            <span>◉</span>
            Markets
          </button>

          <button
            className={`nav-item ${
              activePage === "scanner" ? "active" : ""
            }`}
            onClick={() => setActivePage("scanner")}
          >
            <span>⌕</span>
            Scanner
          </button>

          <p className="nav-title">TRADING</p>

          <button
            className={`nav-item ${
              activePage === "opportunities" ? "active" : ""
            }`}
            onClick={() => setActivePage("opportunities")}
          >
            <span>◆</span>
            Opportunities
          </button>

          <button
            className={`nav-item ${
              activePage === "portfolio" ? "active" : ""
            }`}
            onClick={() => setActivePage("portfolio")}
          >
            <span>↗</span>
            Portfolio
          </button>

          <button
            className={`nav-item ${
              activePage === "paper-trading" ? "active" : ""
            }`}
            onClick={() => setActivePage("paper-trading")}
          >
            <span>▤</span>
            Paper Trading
          </button>

          <p className="nav-title">INTELLIGENCE</p>

          <button
            className={`nav-item ${
              activePage === "agents" ? "active" : ""
            }`}
            onClick={() => setActivePage("agents")}
          >
            <span>✦</span>
            AI Agents
          </button>

          <button
            className={`nav-item ${
              activePage === "analytics" ? "active" : ""
            }`}
            onClick={() => setActivePage("analytics")}
          >
            <span>◌</span>
            Analytics
          </button>

        </nav>

        <div className="sidebar-bottom">

          <button
            className={`nav-item ${
              activePage === "settings" ? "active" : ""
            }`}
            onClick={() => setActivePage("settings")}
          >
            <span>⚙</span>
            Settings
          </button>

          <div className="system-status">

            <span className="status-dot"></span>

            <div>
              <strong>System Online</strong>
              <small>AI Engine Active</small>
            </div>

          </div>

        </div>

      </aside>


      {/* =========================================
          MAIN CONTENT
      ========================================= */}

      <main className="main-content">

        {/* =====================================
            TOP BAR
        ===================================== */}

        <header className="topbar">

          <div>
            <span className="breadcrumb">
              Trading AI /
            </span>

            <strong>
              {activePage === "dashboard"
                ? "Dashboard"
                : activePage === "scanner"
                ? "Market Scanner"
                : activePage === "markets"
                ? "Markets"
                : activePage === "opportunities"
                ? "Opportunities"
                : activePage === "portfolio"
                ? "Portfolio"
                : activePage === "paper-trading"
                ? "Paper Trading"
                : activePage === "agents"
                ? "AI Agents"
                : activePage === "analytics"
                ? "Analytics"
                : activePage === "settings"
                ? "Settings"
                : "Dashboard"}
            </strong>
          </div>

          <div className="topbar-right">

            <div className="market-status">
              <span className="status-dot"></span>
              Market Open
            </div>

            <button className="icon-button">
              ⌕
            </button>

            <button className="profile">
              M
            </button>

          </div>

        </header>


        {/* =========================================
            DASHBOARD PAGE
        ========================================= */}

        {activePage === "dashboard" && (

          <section className="dashboard">

            {/* WELCOME */}

            <div className="welcome">

              <div>

                <p className="eyebrow">
                  AI-POWERED MARKET INTELLIGENCE
                </p>

                <h1>
                  Good afternoon.
                </h1>

                <p>
                  Your trading intelligence center is ready.
                </p>

              </div>

              <button
                className="scan-button"
                onClick={scanMarket}
                disabled={scannerLoading}
              >
                {scannerLoading
                  ? "Scanning..."
                  : "✦ Scan Market"}
              </button>

            </div>


            {/* ERROR */}

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}


            {/* =====================================
                STATS
            ===================================== */}

            <div className="stats-grid">

              <div className="stat-card">

                <span className="stat-label">
                  Trading Capital
                </span>

                <strong>
                  {loading
                    ? "Loading..."
                    : formatMoney(capital)}
                </strong>

                <small className="positive">
                  Starting Capital
                </small>

              </div>


              <div className="stat-card">

                <span className="stat-label">
                  Current Balance
                </span>

                <strong>
                  {loading
                    ? "Loading..."
                    : formatMoney(currentBalance)}
                </strong>

                <small
                  className={
                    currentBalance >= capital
                      ? "positive"
                      : "negative"
                  }
                >
                  {capital > 0
                    ? `${currentBalance >= capital ? "+" : ""}${formatMoney(
                        currentBalance - capital
                      )}`
                    : "—"}
                </small>

              </div>


              <div className="stat-card">

                <span className="stat-label">
                  Win Rate
                </span>

                <strong>
                  {loading
                    ? "Loading..."
                    : `${winRate}%`}
                </strong>

                <small>
                  Based on closed trades
                </small>

              </div>


              <div className="stat-card">

                <span className="stat-label">
                  Open Trades
                </span>

                <strong>
                  {loading
                    ? "Loading..."
                    : openTrades}
                </strong>

                <small>
                  {totalTrades} total trades
                </small>

              </div>

            </div>


            {/* =====================================
                MAIN DASHBOARD GRID
            ===================================== */}

            <div className="dashboard-grid">

              {/* PORTFOLIO */}

              <div className="panel chart-panel">

                <div className="panel-header">

                  <div>

                    <span className="panel-label">
                      PORTFOLIO
                    </span>

                    <h2>
                      Performance
                    </h2>

                  </div>

                  <select>

                    <option>7 Days</option>
                    <option>30 Days</option>
                    <option>3 Months</option>

                  </select>

                </div>

                <div className="chart-placeholder">

                  <div className="chart-line"></div>

                  <div className="chart-label label-1">
                    {formatMoney(currentBalance)}
                  </div>

                  <div className="chart-label label-2">
                    {formatMoney(capital)}
                  </div>

                </div>

              </div>


              {/* OPPORTUNITIES */}

              <div className="panel opportunities-panel">

                <div className="panel-header">

                  <div>

                    <span className="panel-label">
                      AI ENGINE
                    </span>

                    <h2>
                      Top Opportunities
                    </h2>

                  </div>

                  <span className="live-badge">
                    LIVE
                  </span>

                </div>

                {opportunities.length === 0 ? (

                  <div className="empty-state">

                    <p>
                      No opportunities available.
                    </p>

                    <small>
                      Click "Scan Market" to analyze the market.
                    </small>

                  </div>

                ) : (

                  opportunities
                    .slice(0, 3)
                    .map((opportunity, index) => (

                      <div
                        className="opportunity"
                        key={`${opportunity.symbol}-${index}`}
                      >

                        <div className="rank">
                          {String(index + 1).padStart(2, "0")}
                        </div>

                        <div className="opportunity-info">

                          <strong>
                            {opportunity.symbol}
                          </strong>

                          <span>
                            {opportunity.trend || "Unknown"}
                            {" · "}
                            R:R{" "}
                            {opportunity.risk_reward ?? "—"}
                          </span>

                        </div>

                        <div
                          className={
                            opportunity.signal === "BUY"
                              ? "buy"
                              : opportunity.signal === "SELL"
                              ? "sell"
                              : "wait"
                          }
                        >

                          <strong>
                            {opportunity.signal}
                          </strong>

                          <span>
                            {formatConfidence(
                              opportunity.confidence
                            )}
                          </span>

                        </div>

                      </div>

                    ))

                )}

                <button
                  className="view-all"
                  onClick={() => setActivePage("scanner")}
                >
                  Open Market Scanner →
                </button>

              </div>

            </div>


            {/* =====================================
                BOTTOM GRID
            ===================================== */}

            <div className="bottom-grid">

              {/* LATEST SIGNALS */}

              <div className="panel">

                <div className="panel-header">

                  <div>

                    <span className="panel-label">
                      SIGNALS
                    </span>

                    <h2>
                      Latest AI Signals
                    </h2>

                  </div>

                </div>

                {signals.length === 0 ? (

                  <div className="empty-state">

                    <p>
                      No signals available.
                    </p>

                    <small>
                      Run the market scanner to generate signals.
                    </small>

                  </div>

                ) : (

                  signals
                    .slice(0, 5)
                    .map((signal, index) => (

                      <div
                        className="signal-row"
                        key={`${signal.symbol}-${index}`}
                      >

                        <strong>
                          {signal.symbol}
                        </strong>

                        <span
                          className={getSignalClass(
                            signal.signal
                          )}
                        >
                          {signal.signal}
                        </span>

                        <span>
                          {formatConfidence(
                            signal.confidence
                          )} confidence
                        </span>

                      </div>

                    ))

                )}

              </div>


              {/* AI SYSTEM */}

              <div className="panel">

                <div className="panel-header">

                  <div>

                    <span className="panel-label">
                      AGENTS
                    </span>

                    <h2>
                      AI System
                    </h2>

                  </div>

                </div>


                <div className="agent-status">

                  <span className="status-dot"></span>

                  <div>
                    <strong>
                      Decision Engine
                    </strong>

                    <small>
                      Analyzing market conditions
                    </small>
                  </div>

                  <span className="agent-active">
                    ACTIVE
                  </span>

                </div>


                <div className="agent-status">

                  <span className="status-dot"></span>

                  <div>
                    <strong>
                      Risk Engine
                    </strong>

                    <small>
                      Risk management ready
                    </small>
                  </div>

                  <span className="agent-active">
                    ACTIVE
                  </span>

                </div>


                <div className="agent-status">

                  <span className="status-dot"></span>

                  <div>
                    <strong>
                      Market Scanner
                    </strong>

                    <small>
                      Ready to scan market
                    </small>
                  </div>

                  <span className="agent-active">
                    ACTIVE
                  </span>

                </div>

              </div>

            </div>

          </section>

        )}


        {/* =========================================
            SCANNER PAGE
        ========================================= */}

        {activePage === "scanner" && (
          <Scanner />
        )}


        {/* =========================================
            PLACEHOLDER PAGES
        ========================================= */}

        {activePage === "markets" && <Markets />}


        {activePage === "opportunities" && <Opportunities />}


        {activePage === "portfolio" && <Portfolio />}


        {activePage === "paper-trading" && <PaperTrading />}


        {activePage === "agents" && (
          <section className="page-content">
            <div className="page-heading">
              <div>
                <p className="eyebrow">
                  ARTIFICIAL INTELLIGENCE
                </p>
                <h1>AI Agents</h1>
                <p>
                  Market, risk, news, options and master agents will be built here.
                </p>
              </div>
            </div>
          </section>
        )}


        {activePage === "analytics" && <Analytics />}


        {activePage === "settings" && (
          <section className="page-content">
            <div className="page-heading">
              <div>
                <p className="eyebrow">
                  CONFIGURATION
                </p>
                <h1>Settings</h1>
                <p>
                  Portfolio and application settings will be managed here.
                </p>
              </div>
            </div>
          </section>
        )}

      </main>

    </div>
  );
}

export default App;
