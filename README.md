# StockPulse SDK

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://vishwaskv362.github.io/stockpulse-sdk/)

**A dynamic, catalog-driven Python client for the [StockPulse API](https://github.com/vishwaskv362/stockpulse-api).** The SDK discovers available endpoints at runtime from the server's catalog registry — no hardcoded routes, no manual wiring.

```python
from stockpulse import StockPulse

client = StockPulse(api_key="your-key")

# Read with pulse
client.pulse.Research.stocks(symbol="RELIANCE")
client.pulse.Market.movers(direction="gainers")

# Write with push
client.push.Portfolio.trades(symbol="TCS", qty=10, side="BUY")
```

**[Read the full documentation](https://vishwaskv362.github.io/stockpulse-sdk/)**

---

## Installation

```bash
pip install stockpulse-sdk
```

Or from source:

```bash
git clone https://github.com/vishwaskv362/stockpulse-sdk.git
cd stockpulse-sdk
pip install .
```

**Requires Python 3.11+** | Only dependency: `httpx`

---

## Key Concepts

### `pulse` — Read Operations

All GET requests go through `client.pulse`. Keyword arguments become query parameters.

```python
# Stock data
stock = client.pulse.Research.stocks(symbol="RELIANCE")

# Screen by criteria
results = client.pulse.Research.screener(sector="IT", min_price=1000)

# Market overview
indices = client.pulse.Market.indices()
gold = client.pulse.Market.commodities(symbol="GOLD")
forex = client.pulse.Market.forex(pair="USDINR")

# Portfolio
holdings = client.pulse.Portfolio.holdings()
performance = client.pulse.Portfolio.performance()

# News & events
headlines = client.pulse.News.headlines(source="ET", limit=5)
events = client.pulse.News.events(event_type="earnings")
```

### `push` — Write Operations

All POST requests go through `client.push`. Keyword arguments become the JSON body.

```python
# Trading
client.push.Portfolio.trades(symbol="TCS", qty=10, side="BUY")
client.push.Portfolio.orders(symbol="HDFC", qty=20, side="BUY", order_type="LIMIT", price=1600.0)

# Portfolio management
client.push.Portfolio.holdings(symbol="WIPRO", qty=100, avg_price=450.0)
client.push.Portfolio.watchlist(symbol="INFY")

# Research
client.push.Research.analysts(symbol="ITC", firm="Motilal Oswal", rating="Buy", target=500.0)
client.push.Research.screener(name="IT Large Cap", sector="IT", min_price=1000)

# News
client.push.News.sentiment(symbol="RELIANCE", score=0.85, summary="Strong Q4 results")
client.push.News.events(title="TCS Q4 Results", event_type="earnings", date="2026-04-10T00:00:00")
```

---

## Environments

The SDK ships with four built-in environments and supports runtime switching.

| Environment | Base URL | Timeout | SSL |
|-------------|----------|---------|-----|
| `dev` | `http://localhost:8000` | 30s | No |
| `sit` | `https://sit.stockpulse.io/api` | 20s | Yes |
| `uat` | `https://uat.stockpulse.io/api` | 15s | Yes |
| `prd` | `https://api.stockpulse.io` | 10s | Yes |

```python
# Start with a specific environment
client = StockPulse(api_key="key", env="uat")

# Switch at runtime (auto-invalidates catalog cache)
client.config.change_env("prd")

# Register custom environments
client.config.register_env("staging", {
    "base_url": "https://staging.internal.co/api",
    "timeout": 20,
})
```

---

## Available Domains & Resources

| Domain | Resource | `pulse` (GET) | `push` (POST) |
|--------|----------|---------------|----------------|
| **Research** | `stocks` | Stock quote and details | — |
| **Research** | `screener` | Screen stocks by criteria | Save screener preset |
| **Research** | `analysts` | Analyst ratings | Submit a rating |
| **Research** | `ipos` | Upcoming and recent IPOs | — |
| **Research** | `mutual_funds` | Mutual fund data | — |
| **Portfolio** | `holdings` | Portfolio holdings with PnL | Add a holding |
| **Portfolio** | `trades` | Trade history | Place a trade |
| **Portfolio** | `orders` | Open and recent orders | Place an order |
| **Portfolio** | `watchlist` | Watchlist | Add to watchlist |
| **Portfolio** | `performance` | Portfolio performance summary | — |
| **Market** | `indices` | Nifty 50, Sensex, Bank Nifty | — |
| **Market** | `sectors` | Sector performance | — |
| **Market** | `movers` | Top gainers and losers | — |
| **Market** | `commodities` | Gold, silver, crude oil, etc. | — |
| **Market** | `forex` | USD/INR, EUR/INR, etc. | — |
| **News** | `headlines` | Market news | — |
| **News** | `sentiment` | Sentiment reports | Submit a report |
| **News** | `events` | Market events calendar | Create an event |

**26 endpoints** across 4 domains — all discovered dynamically from the server catalog.

---

## Runtime Discovery

```python
# Explore available domains and resources
catalog = client.catalog()
print(catalog["domains"])  # ['Market', 'News', 'Portfolio', 'Research']

# Tab completion in IPython/Jupyter
dir(client.pulse)            # → ['Market', 'News', 'Portfolio', 'Research']
dir(client.pulse.Research)   # → ['analysts', 'ipos', 'mutual_funds', 'screener', 'stocks']

# Inspect any endpoint
print(client.pulse.Research.stocks.info)
```

---

## Error Handling

```python
from stockpulse import StockPulse, ApiError, DomainNotFoundError, ResourceNotFoundError

client = StockPulse()

try:
    client.pulse.Research.stocks(symbol="INVALID")
except ApiError as e:
    print(e.status_code)  # 404
    print(e.detail)       # "Stock INVALID not found"

try:
    client.pulse.Crypto.prices()
except DomainNotFoundError as e:
    print(e.available)    # ['Market', 'News', 'Portfolio', 'Research']
```

| Exception | When |
|-----------|------|
| `DomainNotFoundError` | Domain doesn't exist in catalog |
| `ResourceNotFoundError` | Resource doesn't exist in domain (or not for this operation type) |
| `ApiError` | HTTP error (4xx/5xx) or server unreachable (`status_code=0`) |

---

## How It Works

The SDK uses a three-layer proxy chain to resolve dot-notation into HTTP calls:

```
client.pulse.Research.stocks(symbol="RELIANCE")
  │       │        │
  │       │        └─ ResourceProxy  → GET /api/research/stocks?symbol=RELIANCE
  │       └────────── DomainProxy    → finds "Research" in catalog
  └──────────────── OperationProxy → filters to GET methods
```

1. On first access, fetches `GET /catalog` from the API server
2. Parses endpoint metadata and caches it
3. Each dot-access resolves one layer until you reach a callable
4. Calling the resource executes the HTTP request

Changing environments (`client.config.change_env("uat")`) invalidates the cache, so the next call re-discovers endpoints from the new server.

---

## Running the API Server

The SDK needs a running [StockPulse API](https://github.com/vishwaskv362/stockpulse-api) server:

```bash
git clone https://github.com/vishwaskv362/stockpulse-api.git
cd stockpulse-api
docker-compose up
```

This starts PostgreSQL + the API at `http://localhost:8000` with sample data pre-loaded.

---

## Development

```bash
git clone https://github.com/vishwaskv362/stockpulse-sdk.git
cd stockpulse-sdk
uv sync --all-extras

# Run tests (49 tests, all mocked — no server needed)
uv run pytest tests/ -v

# Build docs locally
uv run mkdocs serve
```

---

## Documentation

Full documentation is available at **[vishwaskv362.github.io/stockpulse-sdk](https://vishwaskv362.github.io/stockpulse-sdk/)**, including:

- [Getting Started](https://vishwaskv362.github.io/stockpulse-sdk/getting-started/quickstart/) — Installation and first API call
- [API Catalog](https://vishwaskv362.github.io/stockpulse-sdk/api-reference/catalog-overview/) — Every endpoint with request/response examples
- [SDK Reference](https://vishwaskv362.github.io/stockpulse-sdk/sdk-reference/client/) — Client, ConfigManager, Proxy Chain, Exceptions
- [Architecture](https://vishwaskv362.github.io/stockpulse-sdk/architecture/) — How the proxy chain and catalog discovery work

---

## License

MIT
