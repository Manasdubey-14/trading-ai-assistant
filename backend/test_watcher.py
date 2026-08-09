from app.market.watcher import MarketWatcher


print("Running market watcher...")

results = MarketWatcher.run_once(
    segment="EQUITY_FNO"
)

print("\nResults:")

for result in results:

    print(result)