# StockPulse Client

The main entry point for all API interactions.

## Constructor

```python
from stockpulse import StockPulse

client = StockPulse(api_key="your-key", env="dev")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str \| None` | `None` | Your StockPulse API key |
| `env` | `str` | `"dev"` | Initial environment: `dev`, `sit`, `uat`, `prd`, or any custom registered environment |

## Properties

### `pulse`

**Type:** `OperationProxy`

Access point for all **read operations** (GET endpoints). All keyword arguments are sent as query parameters.

```python
client.pulse.Research.stocks(symbol="RELIANCE")
client.pulse.Market.movers(direction="gainers", limit=3)
client.pulse.Portfolio.performance()
```

### `push`

**Type:** `OperationProxy`

Access point for all **write operations** (POST/PUT endpoints). All keyword arguments are sent as JSON body.

```python
client.push.Portfolio.trades(symbol="TCS", qty=10, side="BUY")
client.push.News.sentiment(symbol="INFY", score=0.8)
```

### `config`

**Type:** `ConfigManager`

Access environment configuration. See [ConfigManager](config.md) for full reference.

```python
client.config.current_env      # "dev"
client.config.base_url         # "http://localhost:8000"
client.config.change_env("uat")
```

## Methods

### `catalog()`

Returns the raw catalog data from the API server.

**Returns:** `dict` with `domains` and `endpoints` keys.

```python
catalog = client.catalog()

print(catalog["domains"])
# ['Market', 'News', 'Portfolio', 'Research']

for ep in catalog["endpoints"]:
    print(f"{ep['method']:4s} {ep['domain']:10s} {ep['resource']:15s} {ep['description']}")
```

**Response structure:**

```json
{
  "domains": ["Market", "News", "Portfolio", "Research"],
  "endpoints": [
    {
      "domain": "Research",
      "resource": "stocks",
      "method": "GET",
      "path": "/api/research/stocks",
      "description": "Get stock quote and details"
    }
  ]
}
```

## Behavior

### Lazy Catalog Loading

The catalog is **not fetched at initialization**. It is loaded on the first access to `client.pulse` or `client.push`:

```python
client = StockPulse()                        # No HTTP call yet
client.pulse.Research.stocks()                # Fetches /catalog, then calls /api/research/stocks
client.pulse.Market.movers()                  # Uses cached catalog — no extra fetch
```

### Environment Switch Invalidation

When you call `client.config.change_env(...)`, the cached catalog is automatically cleared. The next API call re-fetches the catalog from the new environment's server:

```python
client.config.change_env("uat")              # Cache cleared
client.pulse.Research.stocks()                # Re-fetches /catalog from UAT, then calls endpoint
```

### String Representation

```python
print(client)
# StockPulse(env='dev', base_url='http://localhost:8000')
```
