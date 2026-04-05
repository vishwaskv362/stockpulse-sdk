"""StockPulse SDK — dynamic catalog-driven client for StockPulse API."""

from .client import StockPulse
from .config import ConfigManager
from .exceptions import (
    StockPulseError,
    CatalogNotLoadedError,
    DomainNotFoundError,
    ResourceNotFoundError,
    ApiError,
)

__all__ = [
    "StockPulse",
    "ConfigManager",
    "StockPulseError",
    "CatalogNotLoadedError",
    "DomainNotFoundError",
    "ResourceNotFoundError",
    "ApiError",
]

__version__ = "0.1.0"
