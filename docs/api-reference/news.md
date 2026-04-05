# News Domain

Market news, sentiment analysis, and event calendar.

**SDK namespace:** `client.pulse.News.*` (read) / `client.push.News.*` (write)

---

## headlines

Market news headlines from various sources.

### :material-arrow-down: GET — `client.pulse.News.headlines()`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | No | — | Filter by source (case-insensitive): `ET`, `Moneycontrol`, `LiveMint`, `BS` |
| `limit` | int | No | `10` | Maximum number of headlines to return |

```python
result = client.pulse.News.headlines(source="ET", limit=3)
```
```json
{
  "headlines": [
    {
      "id": 1,
      "title": "Nifty crosses 23,400 on strong FII buying",
      "source": "ET",
      "timestamp": "2026-04-05T..."
    },
    {
      "id": 4,
      "title": "IT stocks rally on weak dollar outlook",
      "source": "ET",
      "timestamp": "2026-04-04T..."
    }
  ]
}
```

Headlines are sorted by timestamp (newest first).

---

## sentiment

Sentiment analysis reports for individual stocks.

### :material-arrow-down: GET — `client.pulse.News.sentiment()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Filter by stock symbol. Omit to get all reports. |

```python
result = client.pulse.News.sentiment(symbol="RELIANCE")
```
```json
{
  "reports": [
    {
      "id": 1,
      "symbol": "RELIANCE",
      "score": 0.85,
      "summary": "Strong Q4 results, beat all estimates",
      "created_at": "2026-04-05T..."
    }
  ]
}
```

Reports are sorted by `created_at` (newest first).

### :material-arrow-up: POST — `client.push.News.sentiment()`

Submit a sentiment report for a stock.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Stock symbol |
| `score` | float | Yes | Sentiment score from `-1.0` (very bearish) to `1.0` (very bullish) |
| `summary` | string | No | Brief text summary of sentiment |

```python
result = client.push.News.sentiment(
    symbol="TCS",
    score=0.65,
    summary="Strong deal pipeline, management guidance positive"
)
```
```json
{
  "message": "Sentiment report submitted",
  "report": {
    "id": 2,
    "symbol": "TCS",
    "score": 0.65,
    "summary": "Strong deal pipeline, management guidance positive"
  }
}
```

**Score interpretation:**

| Range | Meaning |
|-------|---------|
| `-1.0` to `-0.5` | Very bearish |
| `-0.5` to `0.0` | Bearish |
| `0.0` | Neutral |
| `0.0` to `0.5` | Bullish |
| `0.5` to `1.0` | Very bullish |

---

## events

Market event calendar — earnings, dividends, splits, IPOs, and policy decisions.

### :material-arrow-down: GET — `client.pulse.News.events()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_type` | string | No | Filter by type: `earnings`, `dividend`, `split`, `ipo`, `policy` |
| `symbol` | string | No | Filter by stock symbol |

=== "All Events"

    ```python
    result = client.pulse.News.events()
    ```
    ```json
    {
      "events": [
        {
          "id": 4,
          "title": "RBI Policy Meeting",
          "event_type": "policy",
          "date": "2026-04-08T...",
          "description": "Bi-monthly monetary policy review",
          "symbol": null
        },
        {
          "id": 2,
          "title": "TCS Q4 Results",
          "event_type": "earnings",
          "date": "2026-04-10T...",
          "description": "Q4 FY26 quarterly results",
          "symbol": "TCS"
        },
        {
          "id": 5,
          "title": "TechVista Solutions IPO",
          "event_type": "ipo",
          "date": "2026-04-10T...",
          "description": "IPO opens for subscription",
          "symbol": "TECHVISTA"
        },
        {
          "id": 1,
          "title": "Reliance Industries Q4 Results",
          "event_type": "earnings",
          "date": "2026-04-18T...",
          "description": "Q4 FY26 quarterly results announcement",
          "symbol": "RELIANCE"
        },
        {
          "id": 3,
          "title": "HDFC Bank Dividend",
          "event_type": "dividend",
          "date": "2026-04-25T...",
          "description": "Final dividend of Rs.19.50 per share",
          "symbol": "HDFC"
        }
      ]
    }
    ```

=== "By Type"

    ```python
    result = client.pulse.News.events(event_type="earnings")
    ```

=== "By Stock"

    ```python
    result = client.pulse.News.events(symbol="RELIANCE")
    ```

Events are sorted by date (nearest first).

### :material-arrow-up: POST — `client.push.News.events()`

Create a market event entry.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Event title |
| `event_type` | string | Yes | `earnings`, `dividend`, `split`, `ipo`, or `policy` |
| `date` | string | Yes | ISO 8601 date string (e.g. `2026-05-01T00:00:00`) |
| `description` | string | No | Event details |
| `symbol` | string | No | Related stock symbol (null for market-wide events like RBI policy) |

```python
result = client.push.News.events(
    title="Infosys Q4 Results",
    event_type="earnings",
    date="2026-04-20T00:00:00",
    description="Q4 FY26 results announcement",
    symbol="INFY"
)
```
```json
{
  "message": "Event created",
  "event": {"id": 6, "title": "Infosys Q4 Results", "event_type": "earnings"}
}
```

**Event types:**

| Type | Description | Examples |
|------|-------------|---------|
| `earnings` | Quarterly/annual results | TCS Q4 Results |
| `dividend` | Dividend announcements | HDFC Bank Final Dividend |
| `split` | Stock splits | 1:5 split |
| `ipo` | IPO subscriptions | TechVista IPO opens |
| `policy` | Regulatory/policy events | RBI Policy Meeting |
