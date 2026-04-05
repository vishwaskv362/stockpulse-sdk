# Architecture

## System Overview

StockPulse is a two-component system: an **API server** that self-documents its endpoints via a catalog registry, and an **SDK** that reads that catalog at runtime to dynamically build a typed client interface.

```mermaid
graph TB
    subgraph API["StockPulse API Server"]
        R1[Research Router] -->|registers| CAT[Catalog Registry]
        R2[Portfolio Router] -->|registers| CAT
        R3[Market Router] -->|registers| CAT
        R4[News Router] -->|registers| CAT
        CAT -->|serves| CATEP["GET /catalog"]
        DB[(PostgreSQL)]
        R1 & R2 & R3 & R4 --> DB
    end

    subgraph SDK["StockPulse SDK"]
        CL[StockPulse Client] --> CM[ConfigManager]
        CL --> CC[CatalogClient]
        CL --> OP1["pulse (OperationProxy)"]
        CL --> OP2["push (OperationProxy)"]
        OP1 --> DP[DomainProxy]
        OP2 --> DP
        DP --> RP[ResourceProxy]
        CM -->|selects env| ENV["environments/*.json"]
    end

    CATEP -.->|"fetches on first use"| CC
    RP -.->|"HTTP GET / POST"| API

    style API fill:#f3e8ff,stroke:#7c3aed
    style SDK fill:#e8f5e9,stroke:#388e3c
```

---

## Module Breakdown

The SDK is composed of six focused modules, each with a single responsibility.

```mermaid
graph LR
    subgraph Public API
        INIT["__init__.py"]
    end

    subgraph Core
        CLIENT["client.py<br/><i>StockPulse</i>"]
        CONFIG["config.py<br/><i>ConfigManager</i>"]
        CATALOG["catalog.py<br/><i>CatalogClient</i>"]
    end

    subgraph Proxy Chain
        PROXY["proxy.py<br/><i>OperationProxy<br/>DomainProxy<br/>ResourceProxy</i>"]
    end

    subgraph Error Handling
        EXC["exceptions.py<br/><i>StockPulseError tree</i>"]
    end

    INIT --> CLIENT
    INIT --> EXC
    CLIENT --> CONFIG
    CLIENT --> CATALOG
    CLIENT --> PROXY
    PROXY --> CATALOG
    PROXY --> EXC

    style INIT fill:#e3f2fd,stroke:#1565c0
    style CLIENT fill:#fff3e0,stroke:#e65100
    style CONFIG fill:#fff3e0,stroke:#e65100
    style CATALOG fill:#fff3e0,stroke:#e65100
    style PROXY fill:#fce4ec,stroke:#c62828
    style EXC fill:#f3e5f5,stroke:#6a1b9a
```

| Module | Class | Responsibility |
|--------|-------|----------------|
| `client.py` | `StockPulse` | Main entry point. Wires together config, catalog, and proxy layers. Exposes `pulse`, `push`, `config`, and `catalog()`. |
| `config.py` | `ConfigManager` | Loads bundled environment JSON files. Handles `change_env()`, `register_env()`, and fires cache invalidation callbacks. |
| `catalog.py` | `CatalogClient` | Fetches `GET /catalog` from the API server, parses endpoint metadata into `Endpoint` dataclasses, and caches results. |
| `proxy.py` | `OperationProxy` | Resolves domain names from `client.pulse.<Domain>`. Filters endpoints by HTTP method (GET for pulse, POST/PUT for push). |
| `proxy.py` | `DomainProxy` | Resolves resource names from `client.pulse.Domain.<resource>`. Searches catalog for matching endpoint. |
| `proxy.py` | `ResourceProxy` | The callable endpoint. Executes HTTP requests and returns parsed JSON. Exposes `.info` for introspection. |
| `exceptions.py` | `StockPulseError` tree | Structured exception hierarchy: `DomainNotFoundError`, `ResourceNotFoundError`, `ApiError`. |

---

## The Proxy Chain

The proxy chain is the core pattern that enables dot-notation access. Each attribute access resolves one layer deeper until you reach a callable.

```mermaid
sequenceDiagram
    participant User
    participant OP as OperationProxy<br/>(client.pulse)
    participant DP as DomainProxy<br/>(.Research)
    participant RP as ResourceProxy<br/>(.stocks)
    participant CC as CatalogClient
    participant API as StockPulse API

    User->>OP: client.pulse.Research
    OP->>CC: ensure catalog loaded
    alt Catalog not loaded
        CC->>API: GET /catalog
        API-->>CC: endpoint list
        CC->>CC: parse & cache
    end
    OP->>OP: find "Research" in domains
    OP-->>DP: return DomainProxy

    User->>DP: .stocks
    DP->>CC: get_endpoint("Research", "stocks", "GET")
    CC-->>DP: Endpoint object
    DP-->>RP: return ResourceProxy

    User->>RP: (symbol="RELIANCE")
    RP->>API: GET /api/research/stocks?symbol=RELIANCE
    API-->>RP: JSON response
    RP-->>User: dict
```

### How Each Layer Maps

| Expression | Layer | What Happens |
|-----------|-------|-------------|
| `client.pulse` | Property | Returns pre-built `OperationProxy(operation="pulse")` |
| `.Research` | `OperationProxy.__getattr__` | Triggers lazy catalog load, validates domain exists, returns `DomainProxy` |
| `.stocks` | `DomainProxy.__getattr__` | Finds endpoint matching domain + resource + allowed HTTP method, returns `ResourceProxy` |
| `(symbol="RELIANCE")` | `ResourceProxy.__call__` | Builds URL, sends HTTP request, returns parsed JSON |

### Operation Method Routing

The operation type determines which HTTP methods are considered when resolving resources:

```mermaid
graph LR
    PULSE["client.pulse"] -->|"allows"| GET["GET endpoints"]
    PUSH["client.push"] -->|"allows"| POST["POST endpoints"]
    PUSH -->|"allows"| PUT["PUT endpoints"]

    style PULSE fill:#e8f5e9,stroke:#388e3c
    style PUSH fill:#fce4ec,stroke:#c62828
    style GET fill:#e8f5e9,stroke:#388e3c
    style POST fill:#fce4ec,stroke:#c62828
    style PUT fill:#fce4ec,stroke:#c62828
```

This is why `client.push.Market.indices` raises `ResourceNotFoundError` — indices only has a GET endpoint, and `push` only looks for POST/PUT.

---

## Environment Switch & Cache Invalidation

When you call `change_env()`, the SDK invalidates its catalog cache to ensure endpoints are re-discovered from the new server.

```mermaid
sequenceDiagram
    participant User
    participant CM as ConfigManager
    participant CC as CatalogClient
    participant API_UAT as UAT Server

    User->>CM: change_env("uat")
    CM->>CM: validate "uat" exists
    CM->>CM: switch active config
    CM->>CC: on_change_callback()
    CC->>CC: invalidate()<br/>clear cache, is_loaded=False

    Note over User,API_UAT: Next API call triggers re-discovery

    User->>CC: (via pulse/push access)
    CC->>API_UAT: GET https://uat.stockpulse.io/api/catalog
    API_UAT-->>CC: catalog response
    CC->>CC: parse & cache
```

Each environment may expose different endpoints. For example, a `dev` server might have debug routes that `prd` doesn't. Cache invalidation ensures the SDK always reflects the correct API surface.

---

## Catalog Discovery

The API server uses an auto-registration pattern. Each router registers its endpoints with the global catalog at import time:

```python
# Inside the API server (e.g., research/router.py)
catalog.register(
    domain="Research",
    resource="stocks",
    method=HttpMethod.GET,
    path="/api/research/stocks",
    description="Get stock quote and details",
    params=[
        ParamInfo(name="symbol", type="string", required=False)
    ],
)
```

The `GET /catalog` endpoint returns all registered entries:

```mermaid
graph TD
    subgraph Registration ["Endpoint Registration (at import time)"]
        E1["GET /api/research/stocks"] -->|register| REG[CatalogRegistry]
        E2["POST /api/portfolio/trades"] -->|register| REG
        E3["GET /api/market/indices"] -->|register| REG
        E4["...26 endpoints total"] -->|register| REG
    end

    subgraph Discovery ["Catalog Discovery (at runtime)"]
        SDK[SDK Client] -->|"GET /catalog"| REG
        REG -->|"JSON response"| SDK
    end

    style Registration fill:#f3e8ff,stroke:#7c3aed
    style Discovery fill:#e8f5e9,stroke:#388e3c
```

### Catalog Entry Structure

Each entry carries enough metadata for the SDK to build its proxy tree:

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

The SDK uses `domain` to build domains, `resource` to build resource accessors, `method` to route between `pulse` and `push`, and `path` to construct the request URL.

---

## File Structure

```
stockpulse-sdk/
├── stockpulse/
│   ├── __init__.py              # Public exports: StockPulse, exceptions
│   ├── client.py                # StockPulse main client class
│   ├── config.py                # ConfigManager + EnvConfig dataclass
│   ├── catalog.py               # CatalogClient — fetch, parse, cache
│   ├── proxy.py                 # Three-layer proxy chain
│   ├── exceptions.py            # Exception hierarchy
│   └── environments/            # Bundled environment configs
│       ├── dev.json
│       ├── sit.json
│       ├── uat.json
│       └── prd.json
├── tests/
│   ├── test_client.py           # End-to-end client tests
│   ├── test_config.py           # ConfigManager unit tests
│   ├── test_catalog.py          # CatalogClient unit tests
│   └── test_proxy.py            # Proxy chain unit tests
├── docs/                        # MkDocs documentation source
├── mkdocs.yml                   # Documentation site config
└── pyproject.toml               # Project metadata and dependencies
```

---

## Design Decisions

### Why a proxy chain instead of code generation?

Code generation requires rebuilding the SDK whenever the API changes. The proxy chain discovers endpoints at runtime — deploy a new endpoint, register it in the catalog, and every SDK instance picks it up on the next catalog load. **Zero SDK releases needed for API changes.**

### Why separate `pulse` and `push`?

Making the operation type explicit prevents accidental mutations. `client.pulse.Portfolio.trades()` is physically incapable of creating a trade — it only resolves to GET endpoints. Write operations require the conscious choice of `client.push`.

### Why lazy catalog loading?

Constructing `StockPulse()` should be instantaneous. The `/catalog` HTTP call only happens when you actually access an endpoint. This means import-time and initialization have zero network overhead.

### Why case-insensitive matching?

Developer ergonomics. During interactive exploration in a REPL or notebook, `client.pulse.research.stocks()` is as valid as `client.pulse.Research.stocks()`. The extra flexibility reduces friction without introducing ambiguity.

### Why JSON files for environments?

Environment configs are static, declarative data — JSON is the natural fit. Bundling them as package data means they ship with the SDK and require no external configuration. The `register_env()` escape hatch handles cases where bundled configs aren't sufficient.
