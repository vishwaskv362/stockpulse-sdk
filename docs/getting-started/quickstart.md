# Quick Start

This guide walks you through your first StockPulse SDK calls.

## Initialize the Client

```python
from stockpulse import StockPulse

client = StockPulse(api_key="your-api-key")
```

The client defaults to the `dev` environment (`http://localhost:8000`). The API catalog is fetched lazily on first use — no explicit setup step.

## Reading Data with `pulse`

`pulse` is for **read operations** (GET requests). All keyword arguments are sent as query parameters.

### Get a stock quote

```python
result = client.pulse.Research.stocks(symbol="RELIANCE")
print(result)
```
```json
{
  "stock": {
    "symbol": "RELIANCE",
    "name": "Reliance Industries Ltd",
    "sector": "Energy",
    "price": 2945.50,
    "change": 32.10,
    "change_pct": 1.10,
    "volume": 8234567,
    "market_cap": "19.92L Cr",
    "pe_ratio": 28.5,
    "week_52_high": 3217.60,
    "week_52_low": 2220.30
  }
}
```

### Get all stocks

```python
result = client.pulse.Research.stocks()
for stock in result["stocks"]:
    print(f"{stock['symbol']}: ₹{stock['price']}")
```

### Get top market movers

```python
gainers = client.pulse.Market.movers(direction="gainers", limit=3)
for m in gainers["movers"]:
    print(f"{m['symbol']}: {m['change_pct']:+.2f}%")
```

### Check your portfolio

```python
holdings = client.pulse.Portfolio.holdings()
for h in holdings["holdings"]:
    print(f"{h['symbol']}: {h['qty']} shares, PnL: ₹{h['pnl']}")
```

## Writing Data with `push`

`push` is for **write operations** (POST requests). All keyword arguments are sent as the JSON request body.

### Place a trade

```python
result = client.push.Portfolio.trades(
    symbol="TCS",
    qty=10,
    side="BUY"
)
print(result)
```
```json
{
  "message": "Trade executed",
  "trade": {
    "id": 1,
    "symbol": "TCS",
    "qty": 10,
    "side": "BUY",
    "price": 3842.75,
    "status": "EXECUTED"
  }
}
```

### Add to watchlist

```python
client.push.Portfolio.watchlist(symbol="INFY")
```

### Submit a sentiment report

```python
client.push.News.sentiment(
    symbol="RELIANCE",
    score=0.85,
    summary="Strong Q4 results, beat all estimates"
)
```

## Discover Available Endpoints

You can explore what's available at runtime:

```python
# List all domains
catalog = client.catalog()
print(catalog["domains"])
# ['Market', 'News', 'Portfolio', 'Research']

# Tab completion works in IPython/Jupyter
dir(client.pulse)           # → ['Market', 'News', 'Portfolio', 'Research']
dir(client.pulse.Research)  # → ['analysts', 'ipos', 'mutual_funds', 'screener', 'stocks']

# Inspect a specific endpoint
print(client.pulse.Research.stocks.info)
# {
#     'domain': 'Research',
#     'resource': 'stocks',
#     'method': 'GET',
#     'path': '/api/research/stocks',
#     'description': 'Get stock quote and details',
#     'params': [...]
# }
```

## Switch Environments

```python
# Switch to UAT
client.config.change_env("uat")
print(client.config.base_url)
# https://uat.stockpulse.io/api

# Switch back to dev
client.config.change_env("dev")
```

Switching environments automatically re-fetches the catalog from the new server.

## Error Handling

```python
from stockpulse import ApiError, DomainNotFoundError

try:
    client.pulse.Research.stocks(symbol="DOESNOTEXIST")
except ApiError as e:
    print(f"HTTP {e.status_code}: {e.detail}")

try:
    client.pulse.InvalidDomain.something()
except DomainNotFoundError as e:
    print(f"Available domains: {e.available}")
```

## Next Steps

- [Environment Configuration](../guides/environments.md) — manage dev/sit/uat/prd
- [API Catalog Reference](../api-reference/catalog-overview.md) — every endpoint in detail
- [Error Handling Guide](../guides/error-handling.md) — all exception types
