# Market Domain

Market-wide data — indices, sector performance, top movers, commodities, and forex rates.

**SDK namespace:** `client.pulse.Market.*` (read only — no write endpoints)

---

## indices

Indian market indices — Nifty 50, Sensex, Bank Nifty, and Nifty Midcap.

### :material-arrow-down: GET — `client.pulse.Market.indices()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Index symbol: `NIFTY50`, `SENSEX`, `BANKNIFTY`, `NIFTYMIDCAP` |

=== "Single Index"

    ```python
    result = client.pulse.Market.indices(symbol="NIFTY50")
    ```
    ```json
    {
      "index": {
        "symbol": "NIFTY50",
        "name": "Nifty 50",
        "value": 23456.70,
        "change": 128.45,
        "change_pct": 0.55,
        "high": 23512.30,
        "low": 23298.10,
        "open": 23328.25
      }
    }
    ```

=== "All Indices"

    ```python
    result = client.pulse.Market.indices()
    ```
    ```json
    {
      "indices": [
        {"symbol": "NIFTY50", "name": "Nifty 50", "value": 23456.70, ...},
        {"symbol": "SENSEX", "name": "BSE Sensex", "value": 77245.30, ...},
        {"symbol": "BANKNIFTY", "name": "Bank Nifty", "value": 49876.50, ...},
        {"symbol": "NIFTYMIDCAP", "name": "Nifty Midcap 100", "value": 45123.80, ...}
      ]
    }
    ```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Index identifier |
| `name` | string | Full index name |
| `value` | float | Current index value |
| `change` | float | Absolute change from previous close |
| `change_pct` | float | Percentage change |
| `high` | float | Day high |
| `low` | float | Day low |
| `open` | float | Opening value |

---

## sectors

Sector-level performance across the market.

### :material-arrow-down: GET — `client.pulse.Market.sectors()`

No parameters. Returns all sectors sorted by performance (best to worst).

```python
result = client.pulse.Market.sectors()
```
```json
{
  "sectors": [
    {"name": "Telecom", "change_pct": 1.78, "top_gainer": "BHARTIARTL", "top_loser": "IDEA"},
    {"name": "Auto", "change_pct": 1.56, "top_gainer": "TATAMOTORS", "top_loser": "MARUTI"},
    {"name": "IT", "change_pct": 1.23, "top_gainer": "INFY", "top_loser": "WIPRO"},
    {"name": "Energy", "change_pct": 0.89, "top_gainer": "RELIANCE", "top_loser": "ONGC"},
    {"name": "FMCG", "change_pct": 0.34, "top_gainer": "ITC", "top_loser": "HUL"},
    {"name": "Pharma", "change_pct": -0.12, "top_gainer": "SUNPHARMA", "top_loser": "DRREDDY"},
    {"name": "Banking", "change_pct": -0.45, "top_gainer": "ICICIBANK", "top_loser": "HDFC"}
  ]
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Sector name |
| `change_pct` | float | Sector-level percentage change |
| `top_gainer` | string | Best performing stock symbol in the sector |
| `top_loser` | string | Worst performing stock symbol in the sector |

---

## movers

Top gainers and losers across all stocks.

### :material-arrow-down: GET — `client.pulse.Market.movers()`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `direction` | string | No | `"gainers"` | `"gainers"` or `"losers"` |
| `limit` | int | No | `5` | Number of results to return |

=== "Top Gainers"

    ```python
    result = client.pulse.Market.movers(direction="gainers", limit=3)
    ```
    ```json
    {
      "direction": "gainers",
      "movers": [
        {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "price": 745.80, "change": 15.40, "change_pct": 2.11},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "price": 1485.60, "change": 22.30, "change_pct": 1.52},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "price": 1098.30, "change": 12.80, "change_pct": 1.18}
      ]
    }
    ```

=== "Top Losers"

    ```python
    result = client.pulse.Market.movers(direction="losers", limit=3)
    ```
    ```json
    {
      "direction": "losers",
      "movers": [
        {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical", "price": 1234.50, "change": -8.70, "change_pct": -0.70},
        {"symbol": "WIPRO", "name": "Wipro Ltd", "price": 465.20, "change": -3.15, "change_pct": -0.67},
        {"symbol": "TCS", "name": "Tata Consultancy Services", "price": 3842.75, "change": -18.90, "change_pct": -0.49}
      ]
    }
    ```

---

## commodities

Commodity prices — gold, silver, crude oil, natural gas, copper.

### :material-arrow-down: GET — `client.pulse.Market.commodities()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Commodity symbol: `GOLD`, `SILVER`, `CRUDEOIL`, `NATURALGAS`, `COPPER` |

=== "Single Commodity"

    ```python
    result = client.pulse.Market.commodities(symbol="GOLD")
    ```
    ```json
    {
      "commodity": {
        "symbol": "GOLD",
        "name": "Gold",
        "price": 72450.00,
        "unit": "per 10g",
        "change": 350.00,
        "change_pct": 0.49
      }
    }
    ```

=== "All Commodities"

    ```python
    result = client.pulse.Market.commodities()
    ```
    ```json
    {
      "commodities": [
        {"symbol": "GOLD", "name": "Gold", "price": 72450.00, "unit": "per 10g", ...},
        {"symbol": "SILVER", "name": "Silver", "price": 85600.00, "unit": "per kg", ...},
        {"symbol": "CRUDEOIL", "name": "Crude Oil", "price": 6780.00, "unit": "per barrel", ...},
        {"symbol": "NATURALGAS", "name": "Natural Gas", "price": 234.50, "unit": "per mmBtu", ...},
        {"symbol": "COPPER", "name": "Copper", "price": 812.40, "unit": "per kg", ...}
      ]
    }
    ```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Commodity identifier |
| `name` | string | Full name |
| `price` | float | Current price |
| `unit` | string | Price unit (e.g. "per 10g", "per barrel") |
| `change` | float | Absolute price change |
| `change_pct` | float | Percentage change |

---

## forex

Foreign exchange rates against the Indian Rupee.

### :material-arrow-down: GET — `client.pulse.Market.forex()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pair` | string | No | Currency pair: `USDINR`, `EURINR`, `GBPINR`, `JPYINR` |

=== "Single Pair"

    ```python
    result = client.pulse.Market.forex(pair="USDINR")
    ```
    ```json
    {
      "forex": {
        "pair": "USDINR",
        "name": "US Dollar / Indian Rupee",
        "rate": 83.45,
        "change": -0.12,
        "change_pct": -0.14
      }
    }
    ```

=== "All Pairs"

    ```python
    result = client.pulse.Market.forex()
    ```
    ```json
    {
      "forex": [
        {"pair": "USDINR", "name": "US Dollar / Indian Rupee", "rate": 83.45, ...},
        {"pair": "EURINR", "name": "Euro / Indian Rupee", "rate": 90.23, ...},
        {"pair": "GBPINR", "name": "British Pound / Indian Rupee", "rate": 105.67, ...},
        {"pair": "JPYINR", "name": "Japanese Yen / Indian Rupee", "rate": 0.5534, ...}
      ]
    }
    ```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `pair` | string | Currency pair code |
| `name` | string | Full pair name |
| `rate` | float | Exchange rate |
| `change` | float | Absolute change |
| `change_pct` | float | Percentage change |
