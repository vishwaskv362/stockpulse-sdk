"""
Dynamic proxy objects that power the pulse/push namespace.

client.pulse.Research.stocks(symbol="RELIANCE")  → GET /api/research/stocks?symbol=RELIANCE
client.push.Portfolio.trades(symbol="TCS", qty=10, side="BUY")  → POST /api/portfolio/trades
"""

import httpx

from .catalog import CatalogClient, Endpoint
from .exceptions import (
    ApiError,
    DomainNotFoundError,
    ResourceNotFoundError,
)

# Maps operation type to HTTP methods
OPERATION_METHODS = {
    "pulse": ["GET"],           # read operations
    "push": ["POST", "PUT"],    # write operations
}


class ResourceProxy:
    """
    The final callable — represents a specific resource in a domain.

    e.g. client.pulse.Research.stocks  → ResourceProxy(domain="Research", resource="stocks", method="GET")
    """

    def __init__(
        self,
        endpoint: Endpoint,
        config_getter,
    ):
        self._endpoint = endpoint
        self._config_getter = config_getter

    def __call__(self, **kwargs) -> dict:
        """Execute the API call."""
        config = self._config_getter()
        url = f"{config.base_url}{self._endpoint.path}"

        try:
            if self._endpoint.method == "GET":
                response = httpx.get(
                    url,
                    params=kwargs,
                    timeout=config.timeout,
                    verify=config.verify_ssl,
                )
            else:
                response = httpx.post(
                    url,
                    json=kwargs,
                    timeout=config.timeout,
                    verify=config.verify_ssl,
                )

            if response.status_code >= 400:
                detail = response.text
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    pass
                raise ApiError(response.status_code, detail)

            return response.json()
        except httpx.ConnectError:
            raise ApiError(0, f"Cannot connect to {config.base_url}. Is the server running?")

    def __repr__(self) -> str:
        return (
            f"ResourceProxy({self._endpoint.method} {self._endpoint.path} "
            f"— {self._endpoint.description})"
        )

    @property
    def info(self) -> dict:
        """Return metadata about this endpoint."""
        return {
            "domain": self._endpoint.domain,
            "resource": self._endpoint.resource,
            "method": self._endpoint.method,
            "path": self._endpoint.path,
            "description": self._endpoint.description,
            "params": self._endpoint.params,
        }


class DomainProxy:
    """
    Namespace for a domain — resolves resource names.

    e.g. client.pulse.Research  → DomainProxy(domain="Research", operation="pulse")
         client.pulse.Research.stocks  → ResourceProxy(...)
    """

    def __init__(
        self,
        domain: str,
        operation: str,
        catalog: CatalogClient,
        config_getter,
    ):
        self._domain = domain
        self._operation = operation
        self._catalog = catalog
        self._config_getter = config_getter

    def __getattr__(self, resource: str) -> "ResourceProxy":
        if resource.startswith("_"):
            raise AttributeError(resource)

        methods = OPERATION_METHODS[self._operation]

        # Try each allowed method for this operation type
        for method in methods:
            endpoint = self._catalog.get_endpoint(self._domain, resource, method)
            if endpoint:
                return ResourceProxy(endpoint, self._config_getter)

        available = self._catalog.get_resources(self._domain)
        raise ResourceNotFoundError(self._domain, resource, available)

    def __repr__(self) -> str:
        resources = self._catalog.get_resources(self._domain)
        return f"DomainProxy(domain='{self._domain}', resources={resources})"

    def __dir__(self) -> list[str]:
        """Enable tab-completion for resources."""
        methods = OPERATION_METHODS[self._operation]
        resources = set()
        for ep in self._catalog.endpoints:
            if (
                ep.domain.lower() == self._domain.lower()
                and ep.method in methods
            ):
                resources.add(ep.resource)
        return sorted(resources)


class OperationProxy:
    """
    Top-level namespace — resolves domain names.

    e.g. client.pulse  → OperationProxy(operation="pulse")
         client.pulse.Research  → DomainProxy(domain="Research", ...)
    """

    def __init__(
        self,
        operation: str,
        catalog: CatalogClient,
        config_getter,
        ensure_catalog,
    ):
        self._operation = operation
        self._catalog = catalog
        self._config_getter = config_getter
        self._ensure_catalog = ensure_catalog

    def __getattr__(self, domain: str) -> "DomainProxy":
        if domain.startswith("_"):
            raise AttributeError(domain)

        self._ensure_catalog()

        # Check if domain exists
        domains = self._catalog.get_domains()
        domain_match = None
        for d in domains:
            if d.lower() == domain.lower():
                domain_match = d
                break

        if not domain_match:
            raise DomainNotFoundError(domain, domains)

        return DomainProxy(
            domain_match,
            self._operation,
            self._catalog,
            self._config_getter,
        )

    def __repr__(self) -> str:
        op_label = "read" if self._operation == "pulse" else "write"
        return f"OperationProxy('{self._operation}' — {op_label} operations)"

    def __dir__(self) -> list[str]:
        """Enable tab-completion for domains."""
        self._ensure_catalog()
        return self._catalog.get_domains()
