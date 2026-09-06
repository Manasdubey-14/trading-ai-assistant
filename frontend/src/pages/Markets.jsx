import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function Markets() {
  const [symbol, setSymbol] = useState("RELIANCE.NS");
  const [stock, setStock] = useState(null);
  const [ema, setEma] = useState(null);
  const [rsi, setRsi] = useState(null);
  const [macd, setMacd] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadStock = async (event) => {
    event?.preventDefault();

    const cleanSymbol = symbol.trim().toUpperCase();

    if (!cleanSymbol) {
      setError("Enter a stock symbol.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const [stockResponse, emaResponse, rsiResponse, macdResponse] =
        await Promise.all([
          fetch(`${API_URL}/stock/${encodeURIComponent(cleanSymbol)}`),
          fetch(`${API_URL}/stock/${encodeURIComponent(cleanSymbol)}/ema`),
          fetch(`${API_URL}/stock/${encodeURIComponent(cleanSymbol)}/rsi`),
          fetch(`${API_URL}/stock/${encodeURIComponent(cleanSymbol)}/macd`),
        ]);

      if (!stockResponse.ok) {
        throw new Error("Stock data request failed");
      }

      const stockData = await stockResponse.json();

      if (stockData?.error) {
        throw new Error(stockData.error);
      }

      setStock(stockData);

      if (emaResponse.ok) {
        setEma(await emaResponse.json());
      } else {
        setEma(null);
      }

      if (rsiResponse.ok) {
        setRsi(await rsiResponse.json());
      } else {
        setRsi(null);
      }

      if (macdResponse.ok) {
        setMacd(await macdResponse.json());
      } else {
        setMacd(null);
      }
    } catch (err) {
      console.error("Market data error:", err);
      setStock(null);
      setEma(null);
      setRsi(null);
      setMacd(null);
      setError(err.message || "Unable to load market data.");
    } finally {
      setLoading(false);
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

  const signalClass = (signal) => {
    if (signal === "Bullish") return "signal-buy";
    if (signal === "Bearish") return "signal-sell";
    return "signal-wait";
  };

  return (
    <section className="page-content">

      {/* Header */}
      <div className="page-heading">
        <div>
          <p className="eyebrow">MARKET INTELLIGENCE</p>

          <h1>Markets</h1>

          <p>
            Search any supported market symbol and inspect live quote and
            technical indicators.
          </p>
        </div>
      </div>


      {/* Search */}
      <div className="panel market-search-panel">

        <form onSubmit={loadStock} className="market-search">

          <input
            type="text"
            value={symbol}
            onChange={(event) => setSymbol(event.target.value)}
            placeholder="Enter symbol e.g. RELIANCE.NS"
            aria-label="Market symbol"
          />

          <button
            type="submit"
            className="scan-button"
            disabled={loading}
          >
            {loading ? "Loading..." : "Search Market"}
          </button>

        </form>

        <div className="symbol-hints">
          <button onClick={() => setSymbol("RELIANCE.NS")}>
            RELIANCE.NS
          </button>

          <button onClick={() => setSymbol("TCS.NS")}>
            TCS.NS
          </button>

          <button onClick={() => setSymbol("INFY.NS")}>
            INFY.NS
          </button>

          <button onClick={() => setSymbol("HDFCBANK.NS")}>
            HDFCBANK.NS
          </button>

          <span>
            Enter any supported Yahoo Finance symbol.
          </span>
        </div>
      </div>


      {/* Error */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      {/* Stock overview */}
      {stock && (
        <>
          <div className="market-overview">

            <div className="panel stock-hero">

              <div>
                <span className="panel-label">INSTRUMENT</span>

                <h2>{stock.symbol}</h2>

                <p>
                  {stock.company || "Company information unavailable"}
                </p>
              </div>

              <div className="stock-price">
                <span>Current Price</span>
                <strong>{formatMoney(stock.current_price)}</strong>
              </div>

            </div>


            <div className="stat-card">

              <span className="stat-label">
                Previous Close
              </span>

              <strong>
                {formatMoney(stock.previous_close)}
              </strong>

            </div>


            <div className="stat-card">

              <span className="stat-label">
                Open
              </span>

              <strong>
                {formatMoney(stock.open)}
              </strong>

            </div>


            <div className="stat-card">

              <span className="stat-label">
                Day High
              </span>

              <strong>
                {formatMoney(stock.day_high)}
              </strong>

            </div>


            <div className="stat-card">

              <span className="stat-label">
                Day Low
              </span>

              <strong>
                {formatMoney(stock.day_low)}
              </strong>

            </div>


            <div className="stat-card">

              <span className="stat-label">
                Volume
              </span>

              <strong>
                {stock.volume != null
                  ? Number(stock.volume).toLocaleString("en-IN")
                  : "—"}
              </strong>

            </div>

          </div>


          {/* Indicators */}
          <div className="indicator-grid">

            <div className="panel indicator-card">

              <div className="panel-header">
                <div>
                  <span className="panel-label">
                    TREND
                  </span>

                  <h2>EMA 20</h2>
                </div>
              </div>

              <div className="indicator-value">
                {ema?.ema != null
                  ? formatMoney(ema.ema)
                  : "—"}
              </div>

              <div className={signalClass(ema?.signal)}>
                {ema?.signal || "Unavailable"}
              </div>

            </div>


            <div className="panel indicator-card">

              <div className="panel-header">
                <div>
                  <span className="panel-label">
                    MOMENTUM
                  </span>

                  <h2>RSI 14</h2>
                </div>
              </div>

              <div className="indicator-value">
                {rsi?.rsi ?? "—"}
              </div>

              <div className={signalClass(
                rsi?.signal === "Oversold"
                  ? "Bullish"
                  : rsi?.signal === "Overbought"
                  ? "Bearish"
                  : "Neutral"
              )}>
                {rsi?.signal || "Unavailable"}
              </div>

            </div>


            <div className="panel indicator-card">

              <div className="panel-header">
                <div>
                  <span className="panel-label">
                    MOMENTUM
                  </span>

                  <h2>MACD</h2>
                </div>
              </div>

              <div className="indicator-value">
                {macd?.macd ?? "—"}
              </div>

              <div className={signalClass(macd?.signal)}>
                {macd?.signal || "Unavailable"}
              </div>

            </div>

          </div>
        </>
      )}

    </section>
  );
}

export default Markets;