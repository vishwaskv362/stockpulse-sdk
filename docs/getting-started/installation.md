# Installation

## Requirements

- Python **3.11** or higher
- A running [StockPulse API](https://github.com/vishwaskv362/stockpulse-api) server

## Install from PyPI

```bash
pip install stockpulse-sdk
```

## Install from Source

```bash
git clone https://github.com/vishwaskv362/stockpulse-sdk.git
cd stockpulse-sdk
pip install .
```

## Install for Development

=== "pip"

    ```bash
    pip install -e ".[dev]"
    ```

=== "uv"

    ```bash
    uv sync --all-extras
    ```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `httpx` | >= 0.27.0 | HTTP client for API calls |

**Dev dependencies:**

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | >= 8.0.0 | Testing framework |
| `pytest-httpx` | >= 0.35.0 | HTTP mocking for tests |

## Setting Up the API Server

The SDK needs a running StockPulse API server to connect to. The easiest way:

```bash
git clone https://github.com/vishwaskv362/stockpulse-api.git
cd stockpulse-api
docker-compose up
```

This starts PostgreSQL + the API at `http://localhost:8000` with sample data pre-loaded.

## Verify Installation

```python
from stockpulse import StockPulse

client = StockPulse()
print(client)
# StockPulse(env='dev', base_url='http://localhost:8000')
```
