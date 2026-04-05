# Architecture

## Overview

The StockPulse SDK is a thin, dynamic client that never hardcodes API endpoints. Instead, it reads the server's `/catalog` endpoint at runtime and builds a namespace tree from the registered entries.

```
┌──────────────────────────────────────────────────────┐
│  StockPulse API Server                               │
│                                                      │
│  Each endpoint registers itself:                     │
│    domain="Research", resource="stocks", method=GET   │
│                                                      │
│  GET /catalog → returns all registered endpoints     │
└────────────────────┬─────────────────────────────────┘
                     │
                     │ HTTP (httpx)
                     ▼
┌──────────────────────────────────────────────────────┐
│  StockPulse SDK                                      │
│                                                      │
│  StockPulse (client.py)                              │
│    ├── ConfigManager (config.py)                     │
│    │     └── reads environments/*.json               │
│    ├── CatalogClient (catalog.py)                    │
│    │     └── fetches & caches /catalog               │
│    ├── pulse → OperationProxy("pulse")               │
│    │     └── GET endpoints only                      │
│    └── push → OperationProxy("push")                 │
│          └── POST/PUT endpoints only                 │
│                                                      │
│  Proxy Chain (proxy.py):                             │
│    OperationProxy → DomainProxy → ResourceProxy      │
│                                                      │
│  Exceptions (exceptions.py):                         │
│    StockPulseError hierarchy                         │
└──────────────────────────────────────────────────────┘
```

## File Structure

```
stockpulse/
├── __init__.py          # Public API: StockPulse + all exceptions
├── client.py            # StockPulse class — main entry point
├── config.py            # ConfigManager + EnvConfig dataclass
├── catalog.py           # CatalogClient — fetches and caches /catalog
├── proxy.py             # OperationProxy / DomainProxy / ResourceProxy
├── exceptions.py        # Exception hierarchy
└── environments/        # Bundled JSON configs
    ├── dev.json
    ├── sit.json
    ├── uat.json
    └── prd.json
```

## Proxy Chain in Detail

The three-layer proxy chain is the heart of the SDK. Each layer resolves one segment of the dot-notation path.

### Layer 1: OperationProxy

**Created by:** `StockPulse.__init__()` — one for `pulse`, one for `push`

**Responsibility:** Resolve domain names. When you access `client.pulse.Research`:

1. Calls `_ensure_catalog()` to lazy-load the catalog if needed
2. Checks if `"Research"` exists in the catalog domains (case-insensitive)
3. Returns a `DomainProxy` for that domain

**Method filter:**

- `pulse` → only considers endpoints with `method = "GET"`
- `push` → only considers endpoints with `method = "POST"` or `"PUT"`

### Layer 2: DomainProxy

**Created by:** `OperationProxy.__getattr__()`

**Responsibility:** Resolve resource names within a domain. When you access `client.pulse.Research.stocks`:

1. Searches the catalog for an endpoint matching `domain="Research"`, `resource="stocks"`, and an allowed HTTP method
2. Returns a `ResourceProxy` wrapping that endpoint

### Layer 3: ResourceProxy

**Created by:** `DomainProxy.__getattr__()`

**Responsibility:** Execute the HTTP request. When you call `client.pulse.Research.stocks(symbol="RELIANCE")`:

1. Reads the current config (base URL, timeout, SSL)
2. Constructs the full URL: `{base_url}{endpoint.path}`
3. For GET: sends `**kwargs` as query parameters
4. For POST: sends `**kwargs` as JSON body
5. Returns the parsed JSON response
6. Raises `ApiError` on HTTP errors or connection failures

## Catalog Loading Flow

```
client = StockPulse()
│
│  # No HTTP call yet — catalog is lazy
│
client.pulse.Research.stocks()
│
├── OperationProxy.__getattr__("Research")
│   │
│   ├── _ensure_catalog()
│   │   │
│   │   └── catalog.is_loaded == False
│   │       │
│   │       └── CatalogClient.load()
│   │           │
│   │           ├── GET http://localhost:8000/catalog
│   │           ├── Parse response into Endpoint objects
│   │           └── Set is_loaded = True
│   │
│   └── Return DomainProxy("Research", "pulse")
│
├── DomainProxy.__getattr__("stocks")
│   │
│   └── catalog.get_endpoint("Research", "stocks", "GET")
│       └── Return ResourceProxy(endpoint)
│
└── ResourceProxy.__call__(symbol="RELIANCE")
    │
    ├── GET http://localhost:8000/api/research/stocks?symbol=RELIANCE
    └── Return parsed JSON
```

## Environment Switch Flow

```
client.config.change_env("uat")
│
├── Validates "uat" exists
├── Updates current environment pointer
├── Fires _on_change_callback
│   └── CatalogClient.invalidate()
│       ├── Clears endpoint cache
│       └── Sets is_loaded = False
│
└── Next API call triggers fresh catalog load from UAT server
```

## Tab Completion

The SDK implements `__dir__()` on both `OperationProxy` and `DomainProxy` to enable IDE autocomplete:

- `dir(client.pulse)` → queries `CatalogClient.get_domains()`
- `dir(client.pulse.Research)` → queries catalog for resources in "Research" domain that have GET endpoints
- `dir(client.push.Portfolio)` → queries catalog for resources in "Portfolio" domain that have POST/PUT endpoints

This means `client.push.Market` won't show `indices` in autocomplete because there's no POST endpoint for indices — only `client.pulse.Market` will.

## Design Decisions

**Why a proxy chain instead of code generation?**
The proxy chain means the SDK never needs to be updated when new endpoints are added to the API. Deploy a new endpoint on the server, register it in the catalog, and the SDK picks it up automatically.

**Why separate `pulse` and `push`?**
Making the operation type explicit in the call prevents accidental writes. `client.pulse.Portfolio.trades()` can never accidentally POST — it's restricted to GET methods only.

**Why lazy loading?**
Creating a `StockPulse()` instance should be cheap. The HTTP call to `/catalog` only happens when you actually need data, not at import time or construction time.

**Why case-insensitive matching?**
Developer convenience. `client.pulse.research.stocks()` and `client.pulse.Research.stocks()` both work, reducing friction during exploration.
