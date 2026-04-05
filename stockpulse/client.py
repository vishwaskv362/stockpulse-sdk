"""
StockPulse SDK — dynamic catalog-driven client library.

Usage:
    from stockpulse import StockPulse

    client = StockPulse(api_key="xxx")              # defaults to 'dev'
    client.config.change_env("uat")                  # switch environment

    # READ
    client.pulse.Research.stocks(symbol="RELIANCE")
    client.pulse.Market.movers(direction="gainers")

    # WRITE
    client.push.Portfolio.trades(symbol="TCS", qty=10, side="BUY")
    client.push.Portfolio.watchlist(symbol="INFY")
"""

from .catalog import CatalogClient
from .config import ConfigManager
from .proxy import OperationProxy


class StockPulse:
    """Main SDK client. Entry point for all StockPulse API interactions."""

    def __init__(self, api_key: str | None = None, env: str = "dev"):
        self._api_key = api_key
        self._catalog = CatalogClient()
        self._config_manager = ConfigManager(default_env=env)

        # Wire up env change → catalog invalidation
        self._config_manager._on_change_callback = self._catalog.invalidate

        # Create operation proxies
        self._pulse = OperationProxy(
            "pulse", self._catalog, self._get_config, self._ensure_catalog
        )
        self._push = OperationProxy(
            "push", self._catalog, self._get_config, self._ensure_catalog
        )

    def _get_config(self):
        """Returns a simple config object for proxies to use."""
        return self._config_manager

    def _ensure_catalog(self) -> None:
        """Lazy-load catalog on first access."""
        if not self._catalog.is_loaded:
            self._catalog.load(
                base_url=self._config_manager.base_url,
                timeout=self._config_manager.timeout,
                verify_ssl=self._config_manager.verify_ssl,
            )

    @property
    def config(self) -> ConfigManager:
        """Access environment configuration."""
        return self._config_manager

    @property
    def pulse(self) -> OperationProxy:
        """Read operations (GET endpoints)."""
        return self._pulse

    @property
    def push(self) -> OperationProxy:
        """Write operations (POST/PUT endpoints)."""
        return self._push

    def catalog(self) -> dict:
        """Return the raw catalog data."""
        self._ensure_catalog()
        return {
            "domains": self._catalog.get_domains(),
            "endpoints": [
                {
                    "domain": ep.domain,
                    "resource": ep.resource,
                    "method": ep.method,
                    "path": ep.path,
                    "description": ep.description,
                }
                for ep in self._catalog.endpoints
            ],
        }

    def __repr__(self) -> str:
        return (
            f"StockPulse(env='{self._config_manager.current_env}', "
            f"base_url='{self._config_manager.base_url}')"
        )
