# Exceptions

All exceptions are importable from the top-level package:

```python
from stockpulse import (
    StockPulseError,
    CatalogNotLoadedError,
    DomainNotFoundError,
    ResourceNotFoundError,
    ApiError,
)
```

## Hierarchy

```
StockPulseError              ← base class, catch-all
├── CatalogNotLoadedError    ← catalog not yet fetched
├── DomainNotFoundError      ← invalid domain name
├── ResourceNotFoundError    ← invalid resource in domain
└── ApiError                 ← HTTP error or connection failure
```

---

## `StockPulseError`

Base class for all SDK exceptions. Catch this to handle any SDK error generically.

```python
try:
    client.pulse.Research.stocks()
except StockPulseError as e:
    log.error(f"SDK error: {e}")
```

---

## `CatalogNotLoadedError`

Raised if the catalog could not be loaded. In normal usage, the SDK handles catalog loading automatically.

---

## `DomainNotFoundError`

Raised when accessing a domain that doesn't exist in the catalog.

| Attribute | Type | Description |
|-----------|------|-------------|
| `domain` | `str` | The requested domain name |
| `available` | `list[str]` | Valid domain names |

```python
try:
    client.pulse.Crypto.prices()
except DomainNotFoundError as e:
    print(e.domain)      # "Crypto"
    print(e.available)   # ["Market", "News", "Portfolio", "Research"]
```

---

## `ResourceNotFoundError`

Raised when accessing a resource that doesn't exist within a domain, or doesn't exist for the given operation type.

| Attribute | Type | Description |
|-----------|------|-------------|
| `domain` | `str` | The parent domain |
| `resource` | `str` | The requested resource name |
| `available` | `list[str]` | Valid resources in that domain for the operation type |

```python
try:
    client.pulse.Research.futures()
except ResourceNotFoundError as e:
    print(e.domain)      # "Research"
    print(e.resource)    # "futures"
    print(e.available)   # ["analysts", "ipos", "mutual_funds", "screener", "stocks"]
```

!!! note
    A resource may exist in `pulse` but not in `push`. For example, `client.pulse.Market.indices` works (GET endpoint exists), but `client.push.Market.indices` raises `ResourceNotFoundError` (no POST endpoint).

---

## `ApiError`

Raised when the API returns an HTTP error response (4xx, 5xx) or when the server is unreachable.

| Attribute | Type | Description |
|-----------|------|-------------|
| `status_code` | `int` | HTTP status code. `0` if the server is unreachable. |
| `detail` | `str` | Error message from the server |

### HTTP Errors

```python
try:
    client.pulse.Research.stocks(symbol="DOESNOTEXIST")
except ApiError as e:
    print(e.status_code)  # 404
    print(e.detail)       # "Stock DOESNOTEXIST not found"
```

### Connection Errors

```python
try:
    client.pulse.Research.stocks()
except ApiError as e:
    print(e.status_code)  # 0
    print(e.detail)       # "Cannot connect to http://localhost:8000. Is the server running?"
```
