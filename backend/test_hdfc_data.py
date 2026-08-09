import yfinance as yf

symbol = "HDFCBANK.NS"

stock = yf.Ticker(symbol)

history = stock.history(
    period="6mo",
    interval="1d",
)

print("Rows:", len(history))
print("Columns:", list(history.columns))
print(history.tail())