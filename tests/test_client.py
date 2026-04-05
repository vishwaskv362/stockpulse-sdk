"""Tests for the StockPulse client."""

from unittest.mock import MagicMock, patch

import pytest

from stockpulse.client import StockPulse


SAMPLE_CATALOG = {
    "endpoints": [
        {
            "domain": "Research",
            "resource": "stocks",
            "method": "GET",
            "path": "/api/research/stocks",
            "description": "Get stock research data",
            "params": [{"name": "symbol", "type": "string"}],
        },
        {
            "domain": "Research",
            "resource": "sectors",
            "method": "GET",
            "path": "/api/research/sectors",
            "description": "Get sector data",
        },
        {
            "domain": "Portfolio",
            "resource": "trades",
            "method": "POST",
            "path": "/api/portfolio/trades",
            "description": "Submit a trade",
        },
    ]
}


def _mock_catalog_load(mock_httpx_get):
    """Configure mock to return sample catalog for catalog load calls."""
    catalog_response = MagicMock()
    catalog_response.json.return_value = SAMPLE_CATALOG
    catalog_response.raise_for_status = MagicMock()
    mock_httpx_get.return_value = catalog_response
    return catalog_response


class TestStockPulseInit:
    def test_default_env_is_dev(self):
        client = StockPulse(api_key="test")
        assert client.config.current_env == "dev"

    def test_custom_env(self):
        client = StockPulse(api_key="test", env="uat")
        assert client.config.current_env == "uat"


class TestPulseOperations:
    @patch("httpx.get")
    def test_pulse_research_stocks(self, mock_get):
        # First call is catalog load, second is the actual API call
        catalog_response = MagicMock()
        catalog_response.json.return_value = SAMPLE_CATALOG
        catalog_response.raise_for_status = MagicMock()

        api_response = MagicMock()
        api_response.status_code = 200
        api_response.json.return_value = {"data": [{"symbol": "RELIANCE"}]}

        mock_get.side_effect = [catalog_response, api_response]

        client = StockPulse(api_key="test")
        result = client.pulse.Research.stocks(symbol="RELIANCE")

        assert result == {"data": [{"symbol": "RELIANCE"}]}
        assert mock_get.call_count == 2
        # Second call is the API call
        mock_get.assert_called_with(
            "http://localhost:8000/api/research/stocks",
            params={"symbol": "RELIANCE"},
            timeout=30,
            verify=False,
        )


class TestPushOperations:
    @patch("httpx.post")
    @patch("httpx.get")
    def test_push_portfolio_trades(self, mock_get, mock_post):
        _mock_catalog_load(mock_get)

        api_response = MagicMock()
        api_response.status_code = 200
        api_response.json.return_value = {"status": "ok", "trade_id": 123}
        mock_post.return_value = api_response

        client = StockPulse(api_key="test")
        result = client.push.Portfolio.trades(symbol="TCS", qty=10, side="BUY")

        assert result == {"status": "ok", "trade_id": 123}
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/portfolio/trades",
            json={"symbol": "TCS", "qty": 10, "side": "BUY"},
            timeout=30,
            verify=False,
        )


class TestEnvSwitchInvalidatesCatalog:
    @patch("httpx.get")
    def test_env_switch_invalidates_catalog(self, mock_get):
        _mock_catalog_load(mock_get)

        client = StockPulse(api_key="test")

        # Trigger catalog load
        _ = client.catalog()
        assert client._catalog.is_loaded is True

        # Switch env - should invalidate catalog
        client.config.change_env("uat")
        assert client._catalog.is_loaded is False

    @patch("httpx.get")
    def test_catalog_reloads_after_env_switch(self, mock_get):
        _mock_catalog_load(mock_get)

        client = StockPulse(api_key="test")

        # Load catalog in dev
        _ = client.catalog()
        assert mock_get.call_count == 1

        # Switch env invalidates, next access reloads
        client.config.change_env("uat")
        _ = client.catalog()
        assert mock_get.call_count == 2


class TestCatalogMethod:
    @patch("httpx.get")
    def test_catalog_returns_raw_data(self, mock_get):
        _mock_catalog_load(mock_get)

        client = StockPulse(api_key="test")
        data = client.catalog()

        assert "domains" in data
        assert "endpoints" in data
        assert sorted(data["domains"]) == ["Portfolio", "Research"]
        assert len(data["endpoints"]) == 3

    @patch("httpx.get")
    def test_catalog_endpoint_structure(self, mock_get):
        _mock_catalog_load(mock_get)

        client = StockPulse(api_key="test")
        data = client.catalog()

        ep = data["endpoints"][0]
        assert "domain" in ep
        assert "resource" in ep
        assert "method" in ep
        assert "path" in ep
        assert "description" in ep


class TestRepr:
    def test_repr(self):
        client = StockPulse(api_key="test")
        r = repr(client)
        assert "dev" in r
        assert "localhost" in r
