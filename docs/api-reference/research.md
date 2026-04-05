# Research Domain

Stock research, screening, analyst ratings, IPOs, and mutual funds.

**SDK namespace:** `client.pulse.Research.*` (read) / `client.push.Research.*` (write)

---

## stocks

Get stock quotes and details for Indian equities.

### :material-arrow-down: GET — `client.pulse.Research.stocks()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Stock symbol (e.g. `RELIANCE`). Omit to get all active stocks. |

=== "Single Stock"

    ```python
    result = client.pulse.Research.stocks(symbol="RELIANCE")
    ```
    ```json
    {
      "stock": {
        "symbol": "RELIANCE",
        "name": "Reliance Industries Ltd",
        "sector": "Energy",
        "price": 2945.50,
        "change": 32.10,
        "change_pct": 1.10,
        "volume": 8234567,
        "market_cap": "19.92L Cr",
        "pe_ratio": 28.5,
        "week_52_high": 3217.60,
        "week_52_low": 2220.30
      }
    }
    ```

=== "All Stocks"

    ```python
    result = client.pulse.Research.stocks()
    ```
    ```json
    {
      "stocks": [
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "sector": "Telecom", "price": 1485.60, ...},
        {"symbol": "HDFC", "name": "HDFC Bank Ltd", "sector": "Banking", "price": 1623.40, ...},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "sector": "Banking", "price": 1098.30, ...},
        ...
      ]
    }
    ```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | NSE stock symbol |
| `name` | string | Full company name |
| `sector` | string | Sector classification (IT, Banking, Energy, FMCG, Pharma, Auto, Telecom) |
| `price` | float | Current market price |
| `change` | float | Absolute price change |
| `change_pct` | float | Percentage change |
| `volume` | int | Trading volume |
| `market_cap` | string | Market capitalization (e.g. "19.92L Cr") |
| `pe_ratio` | float | Price-to-earnings ratio |
| `week_52_high` | float | 52-week high price |
| `week_52_low` | float | 52-week low price |

!!! info "Error: 404"
    If a `symbol` is provided but not found, the API returns HTTP 404.

---

## screener

Screen and filter stocks by criteria, and save screening presets.

### :material-arrow-down: GET — `client.pulse.Research.screener()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sector` | string | No | Filter by sector (case-insensitive). E.g. `IT`, `Banking` |
| `min_price` | float | No | Minimum stock price |
| `max_price` | float | No | Maximum stock price |

```python
# Find IT stocks between ₹1000 and ₹2000
result = client.pulse.Research.screener(sector="IT", min_price=1000, max_price=2000)
```
```json
{
  "results": [
    {"symbol": "INFY", "name": "Infosys Ltd", "sector": "IT", "price": 1567.30, ...}
  ],
  "count": 1
}
```

### :material-arrow-up: POST — `client.push.Research.screener()`

Save a screener preset for reuse.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Preset name |
| `sector` | string | No | Sector filter |
| `min_price` | float | No | Minimum price |
| `max_price` | float | No | Maximum price |

```python
result = client.push.Research.screener(
    name="IT Large Cap",
    sector="IT",
    min_price=1000
)
```
```json
{
  "message": "Screener preset saved",
  "preset": {
    "id": 1,
    "name": "IT Large Cap",
    "sector": "IT",
    "min_price": 1000.0,
    "max_price": null
  }
}
```

---

## analysts

Analyst ratings and price targets for stocks.

### :material-arrow-down: GET — `client.pulse.Research.analysts()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | **Yes** | Stock symbol |

```python
result = client.pulse.Research.analysts(symbol="RELIANCE")
```
```json
{
  "symbol": "RELIANCE",
  "ratings": [
    {"firm": "Morgan Stanley", "rating": "Overweight", "target": 3200.0, "date": "2026-04-05..."},
    {"firm": "Goldman Sachs", "rating": "Buy", "target": 3100.0, "date": "2026-04-05..."}
  ]
}
```

### :material-arrow-up: POST — `client.push.Research.analysts()`

Submit a new analyst rating.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Stock symbol |
| `firm` | string | Yes | Analyst firm name |
| `rating` | string | Yes | Rating (e.g. Buy, Sell, Neutral, Overweight) |
| `target` | float | Yes | Price target |

```python
result = client.push.Research.analysts(
    symbol="ITC",
    firm="Motilal Oswal",
    rating="Buy",
    target=500.0
)
```
```json
{
  "message": "Rating submitted",
  "rating": {"id": 8, "symbol": "ITC", "firm": "Motilal Oswal", "rating": "Buy", "target": 500.0}
}
```

---

## ipos

Upcoming, open, and recently listed IPOs.

### :material-arrow-down: GET — `client.pulse.Research.ipos()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status: `upcoming`, `open`, `closed`, `listed` |

```python
result = client.pulse.Research.ipos(status="upcoming")
```
```json
{
  "ipos": [
    {
      "id": 1,
      "company_name": "TechVista Solutions",
      "symbol": "TECHVISTA",
      "price_band": "320.0-340.0",
      "open_date": "2026-04-10...",
      "close_date": "2026-04-12...",
      "issue_size": "1200 Cr",
      "status": "upcoming"
    },
    {
      "id": 2,
      "company_name": "GreenEnergy Corp",
      "symbol": "GREENENRG",
      "price_band": "450.0-480.0",
      "open_date": "2026-04-15...",
      "close_date": "2026-04-17...",
      "issue_size": "2500 Cr",
      "status": "upcoming"
    }
  ]
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `company_name` | string | Full company name |
| `symbol` | string | Proposed/assigned trading symbol |
| `price_band` | string | IPO price band (low-high) |
| `open_date` | string | Subscription open date |
| `close_date` | string | Subscription close date |
| `issue_size` | string | Total issue size (e.g. "1200 Cr") |
| `status` | string | `upcoming`, `open`, `closed`, or `listed` |

---

## mutual_funds

Mutual fund schemes with NAV, returns, and risk data.

### :material-arrow-down: GET — `client.pulse.Research.mutual_funds()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | Fund category (case-insensitive): `Large Cap`, `Small Cap`, `Flexi Cap`, `Hybrid` |
| `risk_level` | string | No | Risk level: `low`, `moderate`, `high` |

```python
result = client.pulse.Research.mutual_funds(category="Large Cap")
```
```json
{
  "mutual_funds": [
    {
      "id": 1,
      "scheme_name": "Axis Bluechip Fund",
      "fund_house": "Axis MF",
      "category": "Large Cap",
      "nav": 52.34,
      "aum": "34,500 Cr",
      "return_1y": 15.2,
      "return_3y": 12.8,
      "risk_level": "moderate"
    },
    {
      "id": 2,
      "scheme_name": "Mirae Asset Large Cap",
      "fund_house": "Mirae Asset MF",
      "category": "Large Cap",
      "nav": 89.12,
      "aum": "38,200 Cr",
      "return_1y": 18.5,
      "return_3y": 14.1,
      "risk_level": "moderate"
    }
  ]
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `scheme_name` | string | Full scheme name |
| `fund_house` | string | Asset management company |
| `category` | string | Fund category |
| `nav` | float | Net Asset Value |
| `aum` | string | Assets Under Management |
| `return_1y` | float | 1-year return (%) |
| `return_3y` | float | 3-year return (%) |
| `risk_level` | string | `low`, `moderate`, or `high` |
