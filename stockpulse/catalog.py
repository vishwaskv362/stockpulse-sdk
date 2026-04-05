"""Catalog client — fetches and caches the API catalog."""

from dataclasses import dataclass, field

import httpx


@dataclass
class Endpoint:
    domain: str
    resource: str
    method: str
    path: str
    description: str = ""
    params: list[dict] = field(default_factory=list)


class CatalogClient:
    """Fetches the catalog from the API server and caches it."""

    def __init__(self):
        self._endpoints: list[Endpoint] = []
        self._loaded = False

    def load(self, base_url: str, timeout: int, verify_ssl: bool) -> None:
        """Fetch catalog from the server."""
        response = httpx.get(
            f"{base_url}/catalog",
            timeout=timeout,
            verify=verify_ssl,
        )
        response.raise_for_status()
        data = response.json()

        self._endpoints = []
        for entry in data.get("endpoints", []):
            self._endpoints.append(Endpoint(**entry))
        self._loaded = True

    def invalidate(self) -> None:
        """Clear the cached catalog (called on env change)."""
        self._endpoints = []
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def endpoints(self) -> list[Endpoint]:
        return self._endpoints

    def get_endpoint(self, domain: str, resource: str, method: str) -> Endpoint | None:
        for ep in self._endpoints:
            if (
                ep.domain.lower() == domain.lower()
                and ep.resource.lower() == resource.lower()
                and ep.method.upper() == method.upper()
            ):
                return ep
        return None

    def get_domains(self) -> list[str]:
        return sorted(set(ep.domain for ep in self._endpoints))

    def get_resources(self, domain: str) -> list[str]:
        return sorted(set(
            ep.resource
            for ep in self._endpoints
            if ep.domain.lower() == domain.lower()
        ))
