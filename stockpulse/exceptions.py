"""StockPulse SDK exceptions."""


class StockPulseError(Exception):
    """Base exception for StockPulse SDK."""


class CatalogNotLoadedError(StockPulseError):
    """Raised when trying to use the SDK before the catalog is loaded."""


class DomainNotFoundError(StockPulseError):
    """Raised when accessing a domain that doesn't exist in the catalog."""

    def __init__(self, domain: str, available: list[str]):
        self.domain = domain
        self.available = available
        super().__init__(
            f"Domain '{domain}' not found. Available domains: {', '.join(available)}"
        )


class ResourceNotFoundError(StockPulseError):
    """Raised when accessing a resource that doesn't exist in a domain."""

    def __init__(self, domain: str, resource: str, available: list[str]):
        self.domain = domain
        self.resource = resource
        self.available = available
        super().__init__(
            f"Resource '{resource}' not found in domain '{domain}'. "
            f"Available: {', '.join(available)}"
        )


class ApiError(StockPulseError):
    """Raised when the API returns an error response."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API error {status_code}: {detail}")
