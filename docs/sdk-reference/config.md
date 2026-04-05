# ConfigManager

Manages environment configuration for the SDK. Accessible via `client.config`.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `current_env` | `str` | Name of the active environment |
| `base_url` | `str` | Base URL of the active environment |
| `timeout` | `int` | Request timeout in seconds |
| `retries` | `int` | Number of retry attempts |
| `verify_ssl` | `bool` | Whether SSL certificates are verified |

```python
client.config.current_env    # "dev"
client.config.base_url       # "http://localhost:8000"
client.config.timeout        # 30
client.config.retries        # 1
client.config.verify_ssl     # False
```

## Methods

### `change_env(env_name)`

Switch to a different environment. **Automatically invalidates the catalog cache.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `env_name` | `str` | Environment name |

```python
client.config.change_env("prd")
```

**Raises:** `ValueError` if the environment name is not recognized.

```python
try:
    client.config.change_env("invalid")
except ValueError as e:
    print(e)
    # Unknown environment 'invalid'. Available: dev, prd, sit, uat
```

---

### `list_envs()`

Returns a sorted list of all registered environment names.

**Returns:** `list[str]`

```python
client.config.list_envs()
# ['dev', 'prd', 'sit', 'uat']
```

---

### `register_env(name, config)`

Register a custom environment at runtime.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Environment name |
| `config` | `dict` | Environment configuration |

**Config dict fields:**

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `base_url` | `str` | Yes | — | API server URL |
| `timeout` | `int` | No | `15` | Timeout in seconds |
| `retries` | `int` | No | `2` | Retry attempts |
| `verify_ssl` | `bool` | No | `True` | SSL verification |

```python
client.config.register_env("staging", {
    "base_url": "https://staging.internal.co/api",
    "timeout": 25,
    "retries": 2,
    "verify_ssl": False,
})
client.config.change_env("staging")
```

---

### `get_env_details(env_name=None)`

Returns the full configuration dictionary for an environment.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `env_name` | `str \| None` | `None` | Environment name. Defaults to current environment if omitted. |

**Returns:** `dict`

```python
client.config.get_env_details()
# {'name': 'dev', 'base_url': 'http://localhost:8000', 'timeout': 30, 'retries': 1, 'verify_ssl': False}

client.config.get_env_details("prd")
# {'name': 'prd', 'base_url': 'https://api.stockpulse.io', 'timeout': 10, 'retries': 3, 'verify_ssl': True}
```

**Raises:** `ValueError` if the environment name is not recognized.
