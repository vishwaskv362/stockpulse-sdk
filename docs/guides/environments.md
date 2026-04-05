# Environment Configuration

StockPulse SDK ships with four built-in environments. You can switch between them at runtime, and the SDK automatically handles catalog re-discovery.

## Built-in Environments

| Environment | Base URL | Timeout | Retries | SSL |
|-------------|----------|---------|---------|-----|
| `dev` | `http://localhost:8000` | 30s | 1 | No |
| `sit` | `https://sit.stockpulse.io/api` | 20s | 2 | Yes |
| `uat` | `https://uat.stockpulse.io/api` | 15s | 3 | Yes |
| `prd` | `https://api.stockpulse.io` | 10s | 3 | Yes |

Environment configs are stored as JSON files inside the SDK package at `stockpulse/environments/`.

### Example: `dev.json`

```json
{
    "name": "dev",
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "retries": 1,
    "verify_ssl": false
}
```

## Selecting an Environment

### At Initialization

```python
from stockpulse import StockPulse

# Defaults to 'dev'
client = StockPulse(api_key="your-key")

# Start with a specific environment
client = StockPulse(api_key="your-key", env="uat")
```

### Switching at Runtime

```python
client.config.change_env("prd")
print(client.config.current_env)   # → "prd"
print(client.config.base_url)      # → "https://api.stockpulse.io"
```

!!! warning "Catalog Cache Invalidation"
    Calling `change_env()` **automatically invalidates the cached catalog**. The next API call will re-fetch `/catalog` from the new environment's server. This ensures the SDK always reflects the correct endpoints for the active environment — different environments may expose different endpoints.

## Inspecting Configuration

### Current Environment

```python
client.config.current_env    # → "dev"
client.config.base_url       # → "http://localhost:8000"
client.config.timeout        # → 30
client.config.retries        # → 1
client.config.verify_ssl     # → False
```

### List All Environments

```python
client.config.list_envs()
# ['dev', 'prd', 'sit', 'uat']
```

### Get Full Details

```python
# Current environment
client.config.get_env_details()
# {
#     'name': 'dev',
#     'base_url': 'http://localhost:8000',
#     'timeout': 30,
#     'retries': 1,
#     'verify_ssl': False
# }

# Specific environment
client.config.get_env_details("prd")
# {
#     'name': 'prd',
#     'base_url': 'https://api.stockpulse.io',
#     'timeout': 10,
#     'retries': 3,
#     'verify_ssl': True
# }
```

## Custom Environments

Register your own environments at runtime for internal staging servers, custom deployments, etc.

```python
client.config.register_env("staging", {
    "base_url": "https://staging.internal.company.com/api",
    "timeout": 25,
    "retries": 2,
    "verify_ssl": False,
})

client.config.change_env("staging")
# SDK now talks to your staging server
```

### Config Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `base_url` | `str` | Yes | — | API server base URL |
| `timeout` | `int` | No | `15` | Request timeout in seconds |
| `retries` | `int` | No | `2` | Number of retry attempts |
| `verify_ssl` | `bool` | No | `True` | Whether to verify SSL certificates |

!!! tip
    Custom environments persist for the lifetime of the client instance. If you need them across sessions, consider wrapping the setup in a factory function.

## What Happens on Environment Switch

```
client.config.change_env("uat")
        │
        ├── 1. Validates "uat" exists in environment registry
        ├── 2. Updates active environment pointer
        ├── 3. Fires on_change_callback → CatalogClient.invalidate()
        │       └── Clears cached endpoints, sets is_loaded = False
        └── 4. Next API call triggers lazy catalog reload from UAT server
```

This means you can freely switch environments mid-session:

```python
# Check stock on dev
client.config.change_env("dev")
dev_price = client.pulse.Research.stocks(symbol="RELIANCE")

# Compare with production
client.config.change_env("prd")
prd_price = client.pulse.Research.stocks(symbol="RELIANCE")
```
