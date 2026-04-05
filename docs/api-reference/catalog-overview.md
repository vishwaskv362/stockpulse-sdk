# API Catalog Overview

The StockPulse API uses an **auto-registration catalog system**. Every endpoint registers itself with metadata (domain, resource, HTTP method, path, parameters) into a global registry. The SDK reads this registry from the `/catalog` endpoint to dynamically build its namespace.

## How It Works

```
┌──────────────────────────────────────────────────────────────┐
│  StockPulse API Server                                       │
│                                                              │
│  On startup, each endpoint calls catalog.register():         │
│                                                              │
│    catalog.register(                                         │
│        domain="Research",                                    │
│        resource="stocks",                                    │
│        method="GET",                                         │
│        path="/api/research/stocks",                          │
│        description="Get stock quote and details",            │
│        params=[ParamInfo(name="symbol", type="string", ...)] │
│    )                                                         │
│                                                              │
│  GET /catalog  → returns all registered endpoints            │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  StockPulse SDK                                              │
│                                                              │
│  1. Fetches GET /catalog                                     │
│  2. Parses the endpoint list                                 │
│  3. Builds proxy tree:                                       │
│     pulse.Research.stocks → GET /api/research/stocks          │
│     push.Portfolio.trades → POST /api/portfolio/trades        │
└──────────────────────────────────────────────────────────────┘
```

## Catalog Response Structure

`GET /catalog` returns:

```json
{
  "domains": ["Market", "News", "Portfolio", "Research"],
  "endpoints": [
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
  ],
  "total": 26
}
```

You can also filter by domain:

```
GET /catalog?domain=Research
```

## Domain Hierarchy

The API is organized into four domains, each covering a distinct area of stock market data:

```
StockPulse API
├── Research          ← Stock data, analysis, screening
│   ├── stocks            GET / —
│   ├── screener          GET / POST
│   ├── analysts          GET / POST
│   ├── ipos              GET / —
│   └── mutual_funds      GET / —
│
├── Portfolio         ← User portfolio management
│   ├── holdings          GET / POST
│   ├── trades            GET / POST
│   ├── orders            GET / POST
│   ├── watchlist         GET / POST
│   └── performance       GET / —
│
├── Market            ← Market-wide data
│   ├── indices           GET / —
│   ├── sectors           GET / —
│   ├── movers            GET / —
│   ├── commodities       GET / —
│   └── forex             GET / —
│
└── News              ← Market news and events
    ├── headlines         GET / —
    ├── sentiment         GET / POST
    └── events            GET / POST
```

## Endpoint Count by Domain

| Domain | GET (pulse) | POST (push) | Total |
|--------|-------------|-------------|-------|
| Research | 5 | 2 | 7 |
| Portfolio | 5 | 4 | 9 |
| Market | 5 | 0 | 5 |
| News | 3 | 2 | 5 |
| **Total** | **18** | **8** | **26** |

## SDK Mapping

| SDK Call | HTTP Method | API Path |
|----------|-------------|----------|
| `client.pulse.Research.stocks()` | GET | `/api/research/stocks` |
| `client.push.Research.screener()` | POST | `/api/research/screener` |
| `client.pulse.Portfolio.holdings()` | GET | `/api/portfolio/holdings` |
| `client.push.Portfolio.trades()` | POST | `/api/portfolio/trades` |
| `client.pulse.Market.indices()` | GET | `/api/market/indices` |
| `client.pulse.News.headlines()` | GET | `/api/news/headlines` |
| `client.push.News.sentiment()` | POST | `/api/news/sentiment` |

## Runtime Discovery

You don't need to memorize any of this. The SDK lets you explore at runtime:

```python
# All domains
catalog = client.catalog()
print(catalog["domains"])

# All endpoints with details
for ep in catalog["endpoints"]:
    print(f"{ep['method']:4s} {ep['domain']:10s} {ep['resource']}")

# Tab completion in IPython
dir(client.pulse)            # domains
dir(client.pulse.Research)   # resources in Research (GET only)
dir(client.push.Portfolio)   # resources in Portfolio (POST only)

# Endpoint metadata
print(client.pulse.Research.stocks.info)
```

## Seed Data

The API server auto-seeds the database with sample data on first startup:

| Data | Count | Examples |
|------|-------|---------|
| Stocks | 10 | RELIANCE, TCS, INFY, HDFC, ITC, WIPRO, BHARTIARTL, TATAMOTORS, SUNPHARMA, ICICIBANK |
| Analyst Ratings | 7 | Morgan Stanley on RELIANCE, JP Morgan on TCS, UBS on INFY |
| IPOs | 3 | TechVista (upcoming), GreenEnergy (upcoming), FinServe (listed) |
| Mutual Funds | 5 | Axis Bluechip, Mirae Asset Large Cap, Parag Parikh Flexi Cap |
| Holdings | 3 | RELIANCE (50 shares), TCS (20), ITC (200) in default portfolio |
| Watchlist | 3 | INFY, HDFC, BHARTIARTL |
| Indices | 4 | NIFTY50, SENSEX, BANKNIFTY, NIFTYMIDCAP |
| Sectors | 7 | IT, Banking, Energy, FMCG, Pharma, Auto, Telecom |
| Commodities | 5 | GOLD, SILVER, CRUDEOIL, NATURALGAS, COPPER |
| Forex Pairs | 4 | USDINR, EURINR, GBPINR, JPYINR |
| Headlines | 7 | Market news from ET, Moneycontrol, LiveMint, BS |
| Market Events | 5 | Earnings, dividends, IPO, RBI policy |
