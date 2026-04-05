# StockPulse SDK

**Dynamic, catalog-driven Python client library for the StockPulse API.**

StockPulse SDK discovers available API endpoints automatically from the server's catalog registry. No hardcoded URLs, no manual endpoint wiring — just clean, dot-notation access to Indian stock market data.

---

## What It Does

```python
from stockpulse import StockPulse

client = StockPulse(api_key="your-key")

# Read data with pulse
stock = client.pulse.Research.stocks(symbol="RELIANCE")
movers = client.pulse.Market.movers(direction="gainers")
gold = client.pulse.Market.commodities(symbol="GOLD")

# Write data with push
client.push.Portfolio.trades(symbol="TCS", qty=10, side="BUY")
client.push.News.sentiment(symbol="INFY", score=0.85, summary="Strong Q4")
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Dynamic Discovery** | SDK reads the `/catalog` endpoint to build its namespace — zero hardcoded routes |
| **`pulse` / `push` Separation** | `pulse` for reads (GET), `push` for writes (POST) — clear intent in every call |
| **Environment Management** | Switch between `dev`, `sit`, `uat`, `prd` with `client.config.change_env()` |
| **Lazy Loading** | Catalog is fetched only on first use, then cached until env changes |
| **Tab Completion** | Full `__dir__` support — domains and resources autocomplete in IPython/Jupyter |
| **Structured Errors** | `DomainNotFoundError`, `ResourceNotFoundError`, `ApiError` with helpful messages |
| **Custom Environments** | Register your own environments at runtime with `register_env()` |

---

## How It Works

```
client.pulse.Research.stocks(symbol="RELIANCE")
  │       │        │          └── keyword args → GET query params
  │       │        └── ResourceProxy → resolves to GET /api/research/stocks
  │       └── DomainProxy → finds "Research" in catalog
  └── OperationProxy → filters to GET methods only
```

The SDK uses a three-layer proxy chain. When you access `client.pulse`, it returns an `OperationProxy` that knows it should only look for GET endpoints. Accessing `.Research` returns a `DomainProxy` filtered to that domain. Accessing `.stocks` returns a `ResourceProxy` — the actual callable that makes the HTTP request.

---

## Domains at a Glance

| Domain | What It Covers | pulse (read) | push (write) |
|--------|---------------|-------------|--------------|
| **Research** | Stocks, screeners, analyst ratings, IPOs, mutual funds | 5 endpoints | 2 endpoints |
| **Portfolio** | Holdings, trades, orders, watchlist, performance | 5 endpoints | 4 endpoints |
| **Market** | Indices, sectors, movers, commodities, forex | 5 endpoints | — |
| **News** | Headlines, sentiment analysis, market events | 3 endpoints | 2 endpoints |

**Total: 26 API endpoints** across 4 domains, all auto-discovered.

---

## Quick Links

- [Installation](getting-started/installation.md) — Get up and running in 30 seconds
- [Quick Start](getting-started/quickstart.md) — Your first API call
- [API Catalog](api-reference/catalog-overview.md) — Every endpoint explained
- [Environment Config](guides/environments.md) — dev, sit, uat, prd setup
- [Architecture](architecture.md) — How the proxy chain works under the hood
