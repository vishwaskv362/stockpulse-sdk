# Error Handling

The SDK provides a structured exception hierarchy so you can catch errors at the right level of specificity.

## Exception Hierarchy

```
StockPulseError
├── CatalogNotLoadedError
├── DomainNotFoundError
├── ResourceNotFoundError
└── ApiError
```

All exceptions inherit from `StockPulseError`, so you can catch everything with a single `except` or handle specific cases.

## Exception Types

### `StockPulseError`

Base class for all SDK exceptions.

```python
from stockpulse import StockPulseError

try:
    client.pulse.Research.stocks()
except StockPulseError as e:
    # Catches any SDK error
    print(f"Something went wrong: {e}")
```

---

### `DomainNotFoundError`

Raised when you access a domain that doesn't exist in the catalog.

| Attribute | Type | Description |
|-----------|------|-------------|
| `domain` | `str` | The domain name you tried to access |
| `available` | `list[str]` | List of valid domain names |

```python
from stockpulse import DomainNotFoundError

try:
    client.pulse.Crypto.prices()  # "Crypto" doesn't exist
except DomainNotFoundError as e:
    print(f"Domain '{e.domain}' not found")
    print(f"Available domains: {e.available}")
    # Available domains: ['Market', 'News', 'Portfolio', 'Research']
```

!!! note
    Domain matching is **case-insensitive**. `client.pulse.research` and `client.pulse.Research` both work.

---

### `ResourceNotFoundError`

Raised when you access a resource that doesn't exist within a valid domain.

| Attribute | Type | Description |
|-----------|------|-------------|
| `domain` | `str` | The parent domain name |
| `resource` | `str` | The resource name you tried to access |
| `available` | `list[str]` | List of valid resources in that domain |

```python
from stockpulse import ResourceNotFoundError

try:
    client.pulse.Research.options()  # "options" doesn't exist in Research
except ResourceNotFoundError as e:
    print(f"Resource '{e.resource}' not found in '{e.domain}'")
    print(f"Available: {e.available}")
    # Available: ['analysts', 'ipos', 'mutual_funds', 'screener', 'stocks']
```

!!! important
    A resource might exist in `pulse` but not in `push`, or vice versa. For example, `client.pulse.Market.indices` works (GET), but `client.push.Market.indices` raises `ResourceNotFoundError` because there's no POST endpoint for indices.

---

### `ApiError`

Raised when the API server returns an HTTP error (4xx/5xx) or is unreachable.

| Attribute | Type | Description |
|-----------|------|-------------|
| `status_code` | `int` | HTTP status code (`0` if server is unreachable) |
| `detail` | `str` | Error message from the server |

```python
from stockpulse import ApiError

try:
    client.pulse.Research.stocks(symbol="DOESNOTEXIST")
except ApiError as e:
    if e.status_code == 404:
        print("Stock not found")
    elif e.status_code == 0:
        print("Cannot connect to server — is it running?")
    else:
        print(f"HTTP {e.status_code}: {e.detail}")
```

#### Connection Errors

When the API server is unreachable, `ApiError` is raised with `status_code=0`:

```python
try:
    client.pulse.Research.stocks()
except ApiError as e:
    print(e.status_code)  # → 0
    print(e.detail)       # → "Cannot connect to http://localhost:8000. Is the server running?"
```

---

### `CatalogNotLoadedError`

Defined in the SDK but currently raised only in edge cases. The SDK handles catalog loading automatically via lazy initialization, so you typically won't encounter this.

---

## Recommended Patterns

### Catch-all for production

```python
from stockpulse import StockPulse, StockPulseError, ApiError

client = StockPulse(api_key="xxx")

try:
    data = client.pulse.Research.stocks(symbol="RELIANCE")
except ApiError as e:
    if e.status_code == 0:
        log.error("API server unreachable")
    else:
        log.error(f"API error {e.status_code}: {e.detail}")
except StockPulseError as e:
    log.error(f"SDK error: {e}")
```

### Graceful domain exploration

```python
from stockpulse import DomainNotFoundError, ResourceNotFoundError

# Try a call, fall back gracefully
try:
    data = client.pulse.Research.futures()
except ResourceNotFoundError as e:
    print(f"'{e.resource}' not available. Try: {e.available}")
```

## Importing Exceptions

All exceptions are available from the top-level package:

```python
from stockpulse import (
    StockPulseError,
    CatalogNotLoadedError,
    DomainNotFoundError,
    ResourceNotFoundError,
    ApiError,
)
```
