"""Environment configuration manager."""

import json
from dataclasses import dataclass
from pathlib import Path


ENV_DIR = Path(__file__).parent / "environments"


@dataclass
class EnvConfig:
    name: str
    base_url: str
    timeout: int
    retries: int
    verify_ssl: bool


class ConfigManager:
    """Manages environment configs and allows switching at runtime."""

    def __init__(self, default_env: str = "dev"):
        self._envs: dict[str, EnvConfig] = {}
        self._current_env: str | None = None
        self._on_change_callback = None

        # Load all bundled environment configs
        self._load_bundled_envs()

        # Set default
        self.change_env(default_env)

    def _load_bundled_envs(self) -> None:
        if not ENV_DIR.exists():
            return
        for env_file in ENV_DIR.glob("*.json"):
            with open(env_file) as f:
                data = json.load(f)
            self._envs[data["name"]] = EnvConfig(**data)

    def change_env(self, env_name: str) -> None:
        """Switch to a different environment. Clears catalog cache."""
        if env_name not in self._envs:
            available = ", ".join(sorted(self._envs.keys()))
            raise ValueError(
                f"Unknown environment '{env_name}'. Available: {available}"
            )
        self._current_env = env_name

        # Notify client to invalidate catalog cache
        if self._on_change_callback:
            self._on_change_callback()

    def register_env(self, name: str, config: dict) -> None:
        """Register a custom environment at runtime."""
        self._envs[name] = EnvConfig(
            name=name,
            base_url=config["base_url"],
            timeout=config.get("timeout", 15),
            retries=config.get("retries", 2),
            verify_ssl=config.get("verify_ssl", True),
        )

    @property
    def current_env(self) -> str:
        return self._current_env

    @property
    def base_url(self) -> str:
        return self._envs[self._current_env].base_url

    @property
    def timeout(self) -> int:
        return self._envs[self._current_env].timeout

    @property
    def retries(self) -> int:
        return self._envs[self._current_env].retries

    @property
    def verify_ssl(self) -> bool:
        return self._envs[self._current_env].verify_ssl

    def list_envs(self) -> list[str]:
        return sorted(self._envs.keys())

    def get_env_details(self, env_name: str | None = None) -> dict:
        name = env_name or self._current_env
        env = self._envs.get(name)
        if not env:
            raise ValueError(f"Unknown environment '{name}'")
        return {
            "name": env.name,
            "base_url": env.base_url,
            "timeout": env.timeout,
            "retries": env.retries,
            "verify_ssl": env.verify_ssl,
        }

    def __repr__(self) -> str:
        return f"ConfigManager(env='{self._current_env}', base_url='{self.base_url}')"
