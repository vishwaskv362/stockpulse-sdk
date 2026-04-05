"""Tests for ConfigManager."""

import pytest

from stockpulse.config import ConfigManager


class TestConfigManagerDefaults:
    def test_default_env_is_dev(self):
        cm = ConfigManager()
        assert cm.current_env == "dev"

    def test_default_base_url(self):
        cm = ConfigManager()
        assert cm.base_url == "http://localhost:8000"

    def test_default_timeout(self):
        cm = ConfigManager()
        assert cm.timeout == 30

    def test_default_retries(self):
        cm = ConfigManager()
        assert cm.retries == 1

    def test_default_verify_ssl(self):
        cm = ConfigManager()
        assert cm.verify_ssl is False


class TestChangeEnv:
    def test_change_env_to_uat(self):
        cm = ConfigManager()
        cm.change_env("uat")
        assert cm.current_env == "uat"
        assert cm.base_url == "https://uat.stockpulse.io/api"
        assert cm.timeout == 15
        assert cm.retries == 3
        assert cm.verify_ssl is True

    def test_change_env_to_prd(self):
        cm = ConfigManager()
        cm.change_env("prd")
        assert cm.current_env == "prd"
        assert cm.base_url == "https://api.stockpulse.io"

    def test_change_env_invalid_raises_value_error(self):
        cm = ConfigManager()
        with pytest.raises(ValueError, match="Unknown environment 'staging'"):
            cm.change_env("staging")


class TestListEnvs:
    def test_list_envs_returns_all(self):
        cm = ConfigManager()
        envs = cm.list_envs()
        assert envs == ["dev", "prd", "sit", "uat"]


class TestRegisterEnv:
    def test_register_custom_env(self):
        cm = ConfigManager()
        cm.register_env("custom", {
            "base_url": "http://custom.example.com",
            "timeout": 5,
            "retries": 1,
            "verify_ssl": False,
        })
        assert "custom" in cm.list_envs()
        cm.change_env("custom")
        assert cm.base_url == "http://custom.example.com"
        assert cm.timeout == 5

    def test_register_env_with_defaults(self):
        cm = ConfigManager()
        cm.register_env("minimal", {"base_url": "http://min.example.com"})
        cm.change_env("minimal")
        assert cm.timeout == 15
        assert cm.retries == 2
        assert cm.verify_ssl is True


class TestOnChangeCallback:
    def test_callback_called_on_env_change(self):
        cm = ConfigManager()
        called = []
        cm._on_change_callback = lambda: called.append(True)
        cm.change_env("uat")
        assert len(called) == 1

    def test_callback_not_called_if_not_set(self):
        cm = ConfigManager()
        # Should not raise even without callback
        cm.change_env("uat")
        assert cm.current_env == "uat"


class TestGetEnvDetails:
    def test_get_current_env_details(self):
        cm = ConfigManager()
        details = cm.get_env_details()
        assert details["name"] == "dev"
        assert details["base_url"] == "http://localhost:8000"

    def test_get_specific_env_details(self):
        cm = ConfigManager()
        details = cm.get_env_details("prd")
        assert details["name"] == "prd"

    def test_get_unknown_env_details_raises(self):
        cm = ConfigManager()
        with pytest.raises(ValueError, match="Unknown environment"):
            cm.get_env_details("nonexistent")
