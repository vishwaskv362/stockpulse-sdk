# StockPulse SDK

A dynamic, catalog-driven Python client library for the StockPulse API. The SDK automatically discovers available endpoints from the server's catalog, giving you a clean, dot-notation interface for both read and write operations -- no hardcoded routes, no manual endpoint wiring.

```
pip install stockpulse-sdk
```

> **Requires Python 3.11+**

---

## Table of Contents

- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [API Reference](#api-reference)
  - [StockPulse Client](#stockpulse-client)
  - [pulse -- Read Operations (GET)](#pulse----read-operations-get)
  - [push -- Write Operations (POST/PUT)](#push----write-operations-postput)
  - [ConfigManager](#configmanager)
- [Available Domains & Resources](#available-domains--resources)
- [Error Handling](#error-handling)
- [Custom Environments](#custom-environments)

---

## Quick Start

```python
from stockpulse import StockPulse

# Initialize the client (defaults to 'dev' environment)
client = StockPulse(api_key="your-api-key")

# Read data with pulse (GET)
stocks = client.pulse.Research.stocks(symbol="RELIANCE")
movers = client.pulse.Market.movers(direction="gainers")
gold = client.pulse.Market.commodities(symbol="GOLD")
ipos = client.pulse.Research.ipos(status="upcoming")

# Write data with push (POST)
trade = client.push.Portfolio.trades(symbol="TCS", qty=10, side="BUY")
client.push.Portfolio.watchlist(symbol="INFY")
```

The SDK fetches the API catalog lazily on first access -- no explicit initialization step needed.

---

## Installation

Install from PyPI:

```bash
pip install stockpulse-sdk
```

Or install from source:

```bash
git clone https://github.com/your-org/stockpulse-sdk.git
cd stockpulse-sdk
pip install .
```

For development:

```bash
pip install -e ".[dev]"
```

### Dependencies

| Package | Version |
|---------|---------|
| `httpx` | >= 0.27.0 |
| `pytest` (dev) | >= 8.0.0 |
| `pytest-httpx` (dev) | >= 0.35.0 |

---

## Environment Configuration

StockPulse SDK ships with four built-in environments:

| Environment | Base URL | Timeout | Retries | SSL Verification |
|-------------|----------|---------|---------|------------------|
| `dev` | `http://localhost:8000` | 30s | 1 | No |
| `sit` | `https://sit.stockpulse.io/api` | 20s | 2 | Yes |
| `uat` | `https://uat.stockpulse.io/api` | 15s | 3 | Yes |
| `prd` | `https://api.stockpulse.io` | 10s | 3 | Yes |

### Selecting an Environment

Pass the environment name at initialization:

```python
client = StockPulse(api_key="your-key", env="uat")
```

### Switching Environments at Runtime

```python
client.config.change_env("prd")
```

Switching environments automatically invalidates the cached API catalog. The next operation will re-fetch the catalog from the new environment's server.

### Listing Environments

```python
client.config.list_envs()
# ['dev', 'prd', 'sit', 'uat']
```

### Inspecting Environment Details

```python
client.config.get_env_details()
# {'name': 'dev', 'base_url': 'http://localhost:8000', 'timeout': 30, 'retries': 1, 'verify_ssl': False}

client.config.get_env_details("prd")
# {'name': 'prd', 'base_url': 'https://api.stockpulse.io', 'timeout': 10, 'retries': 3, 'verify_ssl': True}
```

---

## API Reference

### StockPulse Client

The main entry point for all API interactions.

```python
client = StockPulse(api_key="your-key", env="dev")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str \| None` | `None` | Your StockPulse API key |
| `env` | `str` | `"dev"` | Initial environment (`dev`, `sit`, `uat`, `prd`, or custom) |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `client.config` | `ConfigManager` | Access environment configuration and management |
| `client.pulse` | `OperationProxy` | Read operations (GET endpoints) |
| `client.push` | `OperationProxy` | Write operations (POST/PUT endpoints) |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `client.catalog()` | `dict` | Returns the raw catalog with all domains and endpoints |

```python
catalog = client.catalog()
# {
#     "domains": ["Market", "Portfolio", "Research"],
#     "endpoints": [
#         {"domain": "Research", "resource": "stocks", "method": "GET", "path": "/api/research/stocks", "description": "..."},
#         ...
#     ]
# }
```

---

### `pulse` -- Read Operations (GET)

Access any GET endpoint through dot notation: `client.pulse.<Domain>.<resource>(**params)`.

All keyword arguments are sent as query parameters.

```python
# Research
stock = client.pulse.Research.stocks(symbol="RELIANCE")
ipos = client.pulse.Research.ipos(status="upcoming")
funds = client.pulse.Research.mutual_funds(category="Large Cap")

# Market
gainers = client.pulse.Market.movers(direction="gainers")
gold = client.pulse.Market.commodities(symbol="GOLD")
usd = client.pulse.Market.forex(pair="USDINR")

# Portfolio
perf = client.pulse.Portfolio.performance()
orders = client.pulse.Portfolio.orders(status="PENDING")

# News
events = client.pulse.News.events(event_type="earnings")

# Inspect an endpoint before calling it
print(client.pulse.Research.stocks.info)
# {
#     'domain': 'Research',
#     'resource': 'stocks',
#     'method': 'GET',
#     'path': '/api/research/stocks',
#     'description': '...',
#     'params': [...]
# }
```

Tab completion is fully supported -- `dir(client.pulse)` returns available domains, and `dir(client.pulse.Research)` returns available resources.

---

### `push` -- Write Operations (POST/PUT)

Access any POST/PUT endpoint through dot notation: `client.push.<Domain>.<resource>(**data)`.

All keyword arguments are sent as JSON body.

```python
# Place a trade
result = client.push.Portfolio.trades(symbol="TCS", qty=10, side="BUY")

# Place a limit order
client.push.Portfolio.orders(symbol="HDFC", qty=20, side="BUY", order_type="LIMIT", price=1600.0)

# Add to watchlist
client.push.Portfolio.watchlist(symbol="INFY")

# Submit sentiment report
client.push.News.sentiment(symbol="RELIANCE", score=0.85, summary="Strong Q4")

# Create a market event
client.push.News.events(title="TCS Q4 Results", event_type="earnings", date="2026-04-10T00:00:00")
```

---

### ConfigManager

Manages environment configuration. Accessible via `client.config`.

#### Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `change_env(env_name)` | `env_name: str` | Switch to a different environment; invalidates catalog cache |
| `register_env(name, config)` | `name: str`, `config: dict` | Register a custom environment at runtime |
| `list_envs()` | -- | Returns a sorted list of all available environment names |
| `get_env_details(env_name?)` | `env_name: str \| None` | Returns config dict for the given (or current) environment |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `current_env` | `str` | Name of the active environment |
| `base_url` | `str` | Base URL of the active environment |
| `timeout` | `int` | Request timeout in seconds |
| `retries` | `int` | Number of retry attempts |
| `verify_ssl` | `bool` | Whether SSL certificates are verified |

---

## Available Domains & Resources

The SDK discovers domains and resources dynamically from the server's `/catalog` endpoint. The exact list depends on your API server version, but typical domains include:

| Domain | Resource | `pulse` (GET) | `push` (POST) |
|--------|----------|---------------|----------------|
| **Research** | `stocks` | Get stock quote/details | -- |
| **Research** | `screener` | Screen stocks by criteria | Save a screener preset |
| **Research** | `analysts` | Get analyst ratings | Submit a rating |
| **Research** | `ipos` | Get upcoming/recent IPOs | -- |
| **Research** | `mutual_funds` | Get mutual fund data | -- |
| **Portfolio** | `holdings` | Get portfolio holdings | Add a holding |
| **Portfolio** | `trades` | Get trade history | Place a trade |
| **Portfolio** | `orders` | Get open/recent orders | Place an order |
| **Portfolio** | `watchlist` | Get watchlist | Add to watchlist |
| **Portfolio** | `performance` | Portfolio performance summary | -- |
| **Market** | `indices` | Index data (Nifty, Sensex) | -- |
| **Market** | `sectors` | Sector performance | -- |
| **Market** | `movers` | Top gainers/losers | -- |
| **Market** | `commodities` | Commodity prices (gold, crude) | -- |
| **Market** | `forex` | Forex exchange rates | -- |
| **News** | `headlines` | Market news headlines | -- |
| **News** | `sentiment` | Sentiment analysis | Submit sentiment report |
| **News** | `events` | Market events calendar | Create a market event |

To discover all available endpoints at runtime:

```python
catalog = client.catalog()

# List all domains
print(catalog["domains"])

# List all endpoints
for ep in catalog["endpoints"]:
    print(f'{ep["method"]:4s} {ep["path"]:30s} ({ep["domain"]}.{ep["resource"]})')
```

---

## Error Handling

The SDK provides a structured exception hierarchy. All exceptions inherit from `StockPulseError`.

```python
from stockpulse import (
    StockPulseError,
    CatalogNotLoadedError,
    DomainNotFoundError,
    ResourceNotFoundError,
    ApiError,
)
```

| Exception | When It's Raised |
|-----------|-----------------|
| `StockPulseError` | Base class for all SDK errors |
| `CatalogNotLoadedError` | Attempting to use the SDK before the catalog has been fetched |
| `DomainNotFoundError` | Accessing a domain that does not exist in the catalog |
| `ResourceNotFoundError` | Accessing a resource that does not exist within a domain |
| `ApiError` | The API server returns an HTTP error (4xx/5xx) or is unreachable |

### Exception Attributes

**`DomainNotFoundError`**
- `domain` -- the domain name that was requested
- `available` -- list of valid domain names

**`ResourceNotFoundError`**
- `domain` -- the parent domain name
- `resource` -- the resource name that was requested
- `available` -- list of valid resources in the domain

**`ApiError`**
- `status_code` -- HTTP status code (0 if the server is unreachable)
- `detail` -- error message from the server

### Example

```python
from stockpulse import StockPulse, ApiError, DomainNotFoundError

client = StockPulse(api_key="your-key")

try:
    data = client.pulse.Research.stocks(symbol="RELIANCE")
except DomainNotFoundError as e:
    print(f"Bad domain. Choose from: {e.available}")
except ApiError as e:
    print(f"HTTP {e.status_code}: {e.detail}")
```

---

## Custom Environments

Register a custom environment at runtime using `register_env`:

```python
from stockpulse import StockPulse

client = StockPulse(api_key="your-key")

# Register a custom environment
client.config.register_env("staging", {
    "base_url": "https://staging.internal.company.com/api",
    "timeout": 25,
    "retries": 2,
    "verify_ssl": False,
})

# Switch to it
client.config.change_env("staging")

# Use the SDK as normal -- catalog is fetched from the staging server
data = client.pulse.Research.stocks(symbol="RELIANCE")
```

The `config` dict accepts:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `base_url` | `str` | **required** | The API server base URL |
| `timeout` | `int` | `15` | Request timeout in seconds |
| `retries` | `int` | `2` | Number of retry attempts |
| `verify_ssl` | `bool` | `True` | Whether to verify SSL certificates |

---

## Architecture

```
stockpulse/
    __init__.py          # Public API exports
    client.py            # StockPulse main client class
    config.py            # ConfigManager + EnvConfig dataclass
    catalog.py           # CatalogClient -- fetches & caches /catalog
    proxy.py             # OperationProxy / DomainProxy / ResourceProxy
    exceptions.py        # Exception hierarchy
    environments/        # Bundled environment JSON configs
        dev.json
        sit.json
        uat.json
        prd.json
```

The SDK uses a three-layer proxy chain to resolve dot-notation access into HTTP calls:

1. **`OperationProxy`** (`client.pulse` / `client.push`) -- resolves domain names
2. **`DomainProxy`** (`client.pulse.Research`) -- resolves resource names within a domain
3. **`ResourceProxy`** (`client.pulse.Research.stocks`) -- the callable that executes the HTTP request

The API catalog is fetched lazily on first attribute access and cached until the environment is changed.

---

## License

See [LICENSE](LICENSE) for details.
