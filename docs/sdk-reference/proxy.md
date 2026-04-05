# Proxy Chain

The SDK uses a three-layer proxy pattern to translate dot-notation access into HTTP calls. Understanding this helps with debugging and advanced usage.

## The Chain

```
client.pulse.Research.stocks(symbol="RELIANCE")
   │       │        │           │
   │       │        │           └── **kwargs → query params (GET) or JSON body (POST)
   │       │        │
   │       │        └── ResourceProxy.__call__()
   │       │            Makes the actual HTTP request
   │       │
   │       └── DomainProxy.__getattr__("stocks")
   │           Finds the endpoint in catalog matching domain + resource + method
   │
   └── OperationProxy.__getattr__("Research")
       Validates domain exists, creates DomainProxy
```

## OperationProxy

Returned by `client.pulse` and `client.push`. Resolves domain names.

- **`client.pulse`** — filters to `GET` endpoints only
- **`client.push`** — filters to `POST` and `PUT` endpoints only

### Tab Completion

```python
dir(client.pulse)
# ['Market', 'News', 'Portfolio', 'Research']

dir(client.push)
# ['News', 'Portfolio', 'Research']
# Note: Market has no POST endpoints, so it doesn't appear here
```

### Error Handling

Accessing an invalid domain raises `DomainNotFoundError`:

```python
client.pulse.Crypto  # → DomainNotFoundError
```

---

## DomainProxy

Returned by e.g. `client.pulse.Research`. Resolves resource names within a domain.

### Tab Completion

```python
dir(client.pulse.Research)
# ['analysts', 'ipos', 'mutual_funds', 'screener', 'stocks']

dir(client.push.Research)
# ['analysts', 'screener']
# Only resources with POST endpoints appear
```

### Error Handling

Accessing an invalid resource raises `ResourceNotFoundError`:

```python
client.pulse.Research.options  # → ResourceNotFoundError
```

### Case Insensitivity

Domain and resource matching is case-insensitive:

```python
client.pulse.research.stocks()   # works
client.pulse.RESEARCH.STOCKS()   # works
client.pulse.Research.stocks()   # works
```

---

## ResourceProxy

The final callable. Returned by e.g. `client.pulse.Research.stocks`.

### Calling

```python
# GET — kwargs become query parameters
result = client.pulse.Research.stocks(symbol="RELIANCE")
# → GET /api/research/stocks?symbol=RELIANCE

# POST — kwargs become JSON body
result = client.push.Portfolio.trades(symbol="TCS", qty=10, side="BUY")
# → POST /api/portfolio/trades  body: {"symbol": "TCS", "qty": 10, "side": "BUY"}
```

### `.info` Property

Returns metadata about the endpoint without making an HTTP call:

```python
proxy = client.pulse.Research.stocks
print(proxy.info)
```
```json
{
  "domain": "Research",
  "resource": "stocks",
  "method": "GET",
  "path": "/api/research/stocks",
  "description": "Get stock quote and details",
  "params": [
    {
      "name": "symbol",
      "type": "string",
      "required": false,
      "description": "Stock symbol (e.g. RELIANCE). Omit to get all."
    }
  ]
}
```

### `repr()`

```python
print(client.pulse.Research.stocks)
# ResourceProxy(GET /api/research/stocks — Get stock quote and details)
```

### Error Handling

- **HTTP 4xx/5xx** → `ApiError(status_code, detail)`
- **Connection failure** → `ApiError(0, "Cannot connect to ...")`

---

## Operation Method Mapping

| Operation | Allowed HTTP Methods | Purpose |
|-----------|---------------------|---------|
| `pulse` | `GET` | Read data |
| `push` | `POST`, `PUT` | Write data |

When `DomainProxy` resolves a resource, it tries each allowed method for the operation type. For example, `client.push.Portfolio.trades` looks for a `POST` endpoint first, then `PUT`.
