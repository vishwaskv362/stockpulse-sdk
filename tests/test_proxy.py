"""Tests for proxy objects (OperationProxy, DomainProxy, ResourceProxy)."""

from unittest.mock import MagicMock, patch

import pytest

from stockpulse.catalog import CatalogClient, Endpoint
from stockpulse.exceptions import DomainNotFoundError, ResourceNotFoundError
from stockpulse.proxy import DomainProxy, OperationProxy, ResourceProxy


def _make_config():
    """Create a mock config object."""
    config = MagicMock()
    config.base_url = "http://localhost:8000"
    config.timeout = 30
    config.verify_ssl = False
    return config


def _make_catalog_with_endpoints():
    """Create a CatalogClient pre-loaded with test endpoints."""
    catalog = CatalogClient()
    catalog._endpoints = [
        Endpoint(
            domain="Research",
            resource="stocks",
            method="GET",
            path="/api/research/stocks",
            description="Get stock data",
        ),
        Endpoint(
            domain="Research",
            resource="sectors",
            method="GET",
            path="/api/research/sectors",
            description="Get sector data",
        ),
        Endpoint(
            domain="Portfolio",
            resource="trades",
            method="POST",
            path="/api/portfolio/trades",
            description="Submit a trade",
        ),
    ]
    catalog._loaded = True
    return catalog


class TestResourceProxy:
    @patch("stockpulse.proxy.httpx.get")
    def test_get_call(self, mock_get):
        config = _make_config()
        endpoint = Endpoint(
            domain="Research",
            resource="stocks",
            method="GET",
            path="/api/research/stocks",
            description="Get stock data",
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"symbol": "RELIANCE"}]}
        mock_get.return_value = mock_response

        proxy = ResourceProxy(endpoint, lambda: config)
        result = proxy(symbol="RELIANCE")

        assert result == {"data": [{"symbol": "RELIANCE"}]}
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/research/stocks",
            params={"symbol": "RELIANCE"},
            timeout=30,
            verify=False,
        )

    @patch("stockpulse.proxy.httpx.post")
    def test_post_call(self, mock_post):
        config = _make_config()
        endpoint = Endpoint(
            domain="Portfolio",
            resource="trades",
            method="POST",
            path="/api/portfolio/trades",
            description="Submit a trade",
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response

        proxy = ResourceProxy(endpoint, lambda: config)
        result = proxy(symbol="TCS", qty=10, side="BUY")

        assert result == {"status": "ok"}
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/portfolio/trades",
            json={"symbol": "TCS", "qty": 10, "side": "BUY"},
            timeout=30,
            verify=False,
        )

    @patch("stockpulse.proxy.httpx.get")
    def test_api_error_raised_on_400(self, mock_get):
        from stockpulse.exceptions import ApiError

        config = _make_config()
        endpoint = Endpoint(
            domain="Research",
            resource="stocks",
            method="GET",
            path="/api/research/stocks",
        )
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.json.return_value = {"detail": "Invalid symbol"}
        mock_get.return_value = mock_response

        proxy = ResourceProxy(endpoint, lambda: config)
        with pytest.raises(ApiError) as exc_info:
            proxy(symbol="INVALID")
        assert exc_info.value.status_code == 400

    def test_info_property(self):
        endpoint = Endpoint(
            domain="Research",
            resource="stocks",
            method="GET",
            path="/api/research/stocks",
            description="Get stock data",
            params=[{"name": "symbol"}],
        )
        proxy = ResourceProxy(endpoint, lambda: _make_config())
        info = proxy.info
        assert info["domain"] == "Research"
        assert info["resource"] == "stocks"
        assert info["method"] == "GET"


class TestDomainProxy:
    def test_resolves_resource(self):
        catalog = _make_catalog_with_endpoints()
        config = _make_config()
        domain_proxy = DomainProxy("Research", "pulse", catalog, lambda: config)

        resource_proxy = domain_proxy.stocks
        assert isinstance(resource_proxy, ResourceProxy)

    def test_resource_not_found_raises(self):
        catalog = _make_catalog_with_endpoints()
        config = _make_config()
        domain_proxy = DomainProxy("Research", "pulse", catalog, lambda: config)

        with pytest.raises(ResourceNotFoundError) as exc_info:
            domain_proxy.nonexistent
        assert exc_info.value.domain == "Research"
        assert exc_info.value.resource == "nonexistent"

    def test_private_attr_raises_attribute_error(self):
        catalog = _make_catalog_with_endpoints()
        config = _make_config()
        domain_proxy = DomainProxy("Research", "pulse", catalog, lambda: config)

        with pytest.raises(AttributeError):
            domain_proxy._private

    def test_dir_for_tab_completion(self):
        catalog = _make_catalog_with_endpoints()
        config = _make_config()
        domain_proxy = DomainProxy("Research", "pulse", catalog, lambda: config)

        items = dir(domain_proxy)
        assert "stocks" in items
        assert "sectors" in items
        # trades is POST, not in pulse
        assert "trades" not in items

    def test_dir_for_push_operation(self):
        catalog = _make_catalog_with_endpoints()
        config = _make_config()
        domain_proxy = DomainProxy("Portfolio", "push", catalog, lambda: config)

        items = dir(domain_proxy)
        assert "trades" in items


class TestOperationProxy:
    def test_resolves_domain(self):
        catalog = _make_catalog_with_endpoints()
        config = _make_config()
        ensure_catalog = MagicMock()

        op_proxy = OperationProxy("pulse", catalog, lambda: config, ensure_catalog)
        domain_proxy = op_proxy.Research

        assert isinstance(domain_proxy, DomainProxy)
        ensure_catalog.assert_called_once()

    def test_domain_not_found_raises(self):
        catalog = _make_catalog_with_endpoints()
        config = _make_config()
        ensure_catalog = MagicMock()

        op_proxy = OperationProxy("pulse", catalog, lambda: config, ensure_catalog)

        with pytest.raises(DomainNotFoundError) as exc_info:
            op_proxy.Nonexistent
        assert exc_info.value.domain == "Nonexistent"

    def test_private_attr_raises_attribute_error(self):
        catalog = _make_catalog_with_endpoints()
        config = _make_config()
        ensure_catalog = MagicMock()

        op_proxy = OperationProxy("pulse", catalog, lambda: config, ensure_catalog)

        with pytest.raises(AttributeError):
            op_proxy._internal

    def test_dir_for_tab_completion(self):
        catalog = _make_catalog_with_endpoints()
        config = _make_config()
        ensure_catalog = MagicMock()

        op_proxy = OperationProxy("pulse", catalog, lambda: config, ensure_catalog)
        items = dir(op_proxy)

        assert "Portfolio" in items
        assert "Research" in items
