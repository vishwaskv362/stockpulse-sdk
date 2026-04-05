# Portfolio Domain

Portfolio management — holdings, trade execution, order placement, watchlists, and performance tracking.

**SDK namespace:** `client.pulse.Portfolio.*` (read) / `client.push.Portfolio.*` (write)

---

## holdings

Manage portfolio holdings with real-time PnL calculation.

### :material-arrow-down: GET — `client.pulse.Portfolio.holdings()`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `portfolio_id` | string | No | `"default"` | Portfolio identifier |

```python
result = client.pulse.Portfolio.holdings()
```
```json
{
  "portfolio_id": "default",
  "holdings": [
    {
      "id": 1,
      "symbol": "RELIANCE",
      "qty": 50,
      "avg_price": 2800.00,
      "current_price": 2945.50,
      "pnl": 7275.00
    },
    {
      "id": 2,
      "symbol": "TCS",
      "qty": 20,
      "avg_price": 3700.00,
      "current_price": 3842.75,
      "pnl": 2855.00
    },
    {
      "id": 3,
      "symbol": "ITC",
      "qty": 200,
      "avg_price": 400.00,
      "current_price": 432.15,
      "pnl": 6430.00
    }
  ]
}
```

!!! info "PnL Calculation"
    `pnl = (current_price - avg_price) * qty`

    The `current_price` is fetched from the stocks table in real-time.

### :material-arrow-up: POST — `client.push.Portfolio.holdings()`

Add a new holding to a portfolio.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | Yes | — | Stock symbol |
| `qty` | int | Yes | — | Number of shares |
| `avg_price` | float | Yes | — | Average acquisition price |
| `portfolio_id` | string | No | `"default"` | Portfolio identifier |

```python
result = client.push.Portfolio.holdings(
    symbol="WIPRO",
    qty=100,
    avg_price=450.00
)
```
```json
{
  "message": "Holding added",
  "holding": {"id": 4, "symbol": "WIPRO", "qty": 100, "avg_price": 450.0}
}
```

---

## trades

Execute and view trade history.

### :material-arrow-down: GET — `client.pulse.Portfolio.trades()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Filter by stock symbol |

```python
result = client.pulse.Portfolio.trades(symbol="TCS")
```
```json
{
  "trades": [
    {
      "id": 1,
      "symbol": "TCS",
      "qty": 10,
      "side": "BUY",
      "price": 3842.75,
      "status": "EXECUTED",
      "executed_at": "2026-04-05T..."
    }
  ],
  "count": 1
}
```

### :material-arrow-up: POST — `client.push.Portfolio.trades()`

Place a trade. If `price` is omitted, uses the current market price.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Stock symbol |
| `qty` | int | Yes | Number of shares |
| `side` | string | Yes | `BUY` or `SELL` |
| `price` | float | No | Limit price. Omit for market price. |

=== "Market Order"

    ```python
    # Price auto-fetched from current stock price
    result = client.push.Portfolio.trades(symbol="INFY", qty=25, side="BUY")
    ```
    ```json
    {
      "message": "Trade executed",
      "trade": {"id": 2, "symbol": "INFY", "qty": 25, "side": "BUY", "price": 1567.30, "status": "EXECUTED"}
    }
    ```

=== "Limit Order"

    ```python
    result = client.push.Portfolio.trades(symbol="INFY", qty=25, side="BUY", price=1550.00)
    ```
    ```json
    {
      "message": "Trade executed",
      "trade": {"id": 3, "symbol": "INFY", "qty": 25, "side": "BUY", "price": 1550.00, "status": "EXECUTED"}
    }
    ```

---

## orders

Place and manage orders (market, limit, stop-loss).

### :material-arrow-down: GET — `client.pulse.Portfolio.orders()`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status: `PENDING`, `EXECUTED`, `CANCELLED` |

```python
result = client.pulse.Portfolio.orders(status="PENDING")
```
```json
{
  "orders": [
    {
      "id": 1,
      "symbol": "HDFC",
      "qty": 20,
      "side": "BUY",
      "order_type": "LIMIT",
      "price": 1600.00,
      "trigger_price": null,
      "status": "PENDING",
      "created_at": "2026-04-05T..."
    }
  ],
  "count": 1
}
```

### :material-arrow-up: POST — `client.push.Portfolio.orders()`

Place an order.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | Yes | — | Stock symbol |
| `qty` | int | Yes | — | Number of shares |
| `side` | string | Yes | — | `BUY` or `SELL` |
| `order_type` | string | No | `MARKET` | `MARKET`, `LIMIT`, or `SL` (stop-loss) |
| `price` | float | No | — | Required for `LIMIT` orders |
| `trigger_price` | float | No | — | Required for `SL` orders |

=== "Market Order"

    ```python
    result = client.push.Portfolio.orders(symbol="TCS", qty=5, side="BUY")
    ```

=== "Limit Order"

    ```python
    result = client.push.Portfolio.orders(
        symbol="HDFC", qty=20, side="BUY",
        order_type="LIMIT", price=1600.00
    )
    ```

=== "Stop-Loss Order"

    ```python
    result = client.push.Portfolio.orders(
        symbol="RELIANCE", qty=10, side="SELL",
        order_type="SL", price=2850.00, trigger_price=2900.00
    )
    ```

```json
{
  "message": "Order placed",
  "order": {"id": 1, "symbol": "HDFC", "qty": 20, "side": "BUY", "order_type": "LIMIT", "status": "PENDING"}
}
```

---

## watchlist

Manage stock watchlists.

### :material-arrow-down: GET — `client.pulse.Portfolio.watchlist()`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `list_id` | string | No | `"default"` | Watchlist identifier |

```python
result = client.pulse.Portfolio.watchlist()
```
```json
{
  "list_id": "default",
  "watchlist": [
    {"symbol": "INFY", "name": "Infosys Ltd", "price": 1567.30, "change_pct": 0.80},
    {"symbol": "HDFC", "name": "HDFC Bank Ltd", "price": 1623.40, "change_pct": -0.32},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "price": 1485.60, "change_pct": 1.52}
  ]
}
```

### :material-arrow-up: POST — `client.push.Portfolio.watchlist()`

Add a symbol to a watchlist. Duplicates are silently ignored (idempotent).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | Yes | — | Stock symbol to add |
| `list_id` | string | No | `"default"` | Watchlist identifier |

```python
client.push.Portfolio.watchlist(symbol="TCS")
```
```json
{
  "message": "TCS added to watchlist",
  "list_id": "default"
}
```

---

## performance

Portfolio performance summary with PnL aggregation.

### :material-arrow-down: GET — `client.pulse.Portfolio.performance()`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `portfolio_id` | string | No | `"default"` | Portfolio identifier |

```python
result = client.pulse.Portfolio.performance()
```
```json
{
  "portfolio_id": "default",
  "total_invested": 234000.00,
  "total_current": 250560.00,
  "total_pnl": 16560.00,
  "pnl_pct": 7.08
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total_invested` | float | Sum of `avg_price * qty` across all holdings |
| `total_current` | float | Sum of `current_price * qty` across all holdings |
| `total_pnl` | float | `total_current - total_invested` |
| `pnl_pct` | float | `(total_pnl / total_invested) * 100` |
