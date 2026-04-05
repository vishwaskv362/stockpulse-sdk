"""Tests for CatalogClient."""

from unittest.mock import MagicMock, patch

import pytest

from stockpulse.catalog import CatalogClient, Endpoint


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


class TestCatalogLoad:
    @patch("stockpulse.catalog.httpx.get")
    def test_load_parses_catalog(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_CATALOG
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)

        assert catalog.is_loaded is True
        assert len(catalog.endpoints) == 3
        mock_get.assert_called_once_with(
            "http://localhost:8000/catalog",
            timeout=30,
            verify=False,
        )

    @patch("stockpulse.catalog.httpx.get")
    def test_load_creates_endpoint_objects(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_CATALOG
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)

        ep = catalog.endpoints[0]
        assert isinstance(ep, Endpoint)
        assert ep.domain == "Research"
        assert ep.resource == "stocks"
        assert ep.method == "GET"
        assert ep.path == "/api/research/stocks"

    @patch("stockpulse.catalog.httpx.get")
    def test_load_empty_catalog(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"endpoints": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)

        assert catalog.is_loaded is True
        assert len(catalog.endpoints) == 0


class TestCatalogInvalidate:
    @patch("stockpulse.catalog.httpx.get")
    def test_invalidate_clears_cache(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_CATALOG
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)
        assert catalog.is_loaded is True

        catalog.invalidate()
        assert catalog.is_loaded is False
        assert len(catalog.endpoints) == 0


class TestGetEndpoint:
    @patch("stockpulse.catalog.httpx.get")
    def test_get_endpoint_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_CATALOG
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)

        ep = catalog.get_endpoint("Research", "stocks", "GET")
        assert ep is not None
        assert ep.path == "/api/research/stocks"

    @patch("stockpulse.catalog.httpx.get")
    def test_get_endpoint_case_insensitive(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_CATALOG
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)

        ep = catalog.get_endpoint("research", "STOCKS", "get")
        assert ep is not None
        assert ep.domain == "Research"

    @patch("stockpulse.catalog.httpx.get")
    def test_get_endpoint_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_CATALOG
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)

        ep = catalog.get_endpoint("Research", "nonexistent", "GET")
        assert ep is None


class TestGetDomainsAndResources:
    @patch("stockpulse.catalog.httpx.get")
    def test_get_domains(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_CATALOG
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)

        domains = catalog.get_domains()
        assert domains == ["Portfolio", "Research"]

    @patch("stockpulse.catalog.httpx.get")
    def test_get_resources(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_CATALOG
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)

        resources = catalog.get_resources("Research")
        assert resources == ["sectors", "stocks"]

    @patch("stockpulse.catalog.httpx.get")
    def test_get_resources_case_insensitive(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_CATALOG
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)

        resources = catalog.get_resources("research")
        assert resources == ["sectors", "stocks"]

    @patch("stockpulse.catalog.httpx.get")
    def test_get_resources_unknown_domain(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_CATALOG
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        catalog = CatalogClient()
        catalog.load("http://localhost:8000", timeout=30, verify_ssl=False)

        resources = catalog.get_resources("Nonexistent")
        assert resources == []
