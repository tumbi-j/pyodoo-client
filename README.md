# pyodoo-client (Odoo 19+ JSON-2)

Python client for Odoo JSON-2 API (`/json/2`) targeting Odoo 19+.

## Features

- JSON-2 model calls with named payloads.
- ORM-like model access (`client.model("res.partner")`).
- `OdooEntity` convenience wrapper (`save`, `delete`, `refresh`).
- Context layering (`default_context`, `with_context`, per-call `context`).
- Runtime `debug` mode toggle:
  - `debug=False`: returns safe defaults and stores errors.
  - `debug=True`: raises exceptions.
- Database service wrappers for `/web/version` and `/web/database/*`.

## Installation

```bash
pip install pyodoo-client
```

## Important Version Guidance

`pyodoo-client` is for Odoo JSON-2 (`/json/2`) workflows (Odoo 19+).

If your project targets older Odoo versions that still use the classic RPC style, use `pyodoo-rpc-client` instead:

- PyPI: https://pypi.org/project/pyodoo-rpc-client/
- GitHub: https://github.com/tumbi-j/pyodoo-rpc-client

## Quick Start

```python
from pyodoo_client import OdooClient

odoo = OdooClient(
    url="https://mycompany.example.com",
    db="mycompany",
    api_key="YOUR_API_KEY",
    debug=False,
)

partners = odoo.model("res.partner").search_read({
    "context": {"lang": "en_US"},
    "domain": [
        ["name", "ilike", "%deco%"],
        ["is_company", "=", True],
    ],
    "fields": ["name"],
})
```

## API Overview

### OdooClient

- `OdooClient(url, api_key=None, key=None, db=None, timeout=30, verify_ssl=True, user_agent="pyodoo-client", debug=False, default_context=None)`
- `model(model_name)`
- `set_debug(bool)`
- `set_default_context(dict)` / `update_default_context(dict)`
- `call_model(model_name, method, payload=None, context=None, debug=None, default=None)`
- `call_web(method, path, ...)`
- `database` service property

### OdooModel

- `with_context(context=None, **kwargs)`
- `with_company(company)` (alias for setting company context)
- `set_debug(bool)`
- `execute(method, *args, **kwargs)`
- CRUD helpers: `search`, `search_read`, `read`, `create`, `write`, `unlink`, `fields_get`

Context helpers:

```python
partners = odoo.model("res.partner")

# Dict style
partners_en = partners.with_context({"lang": "en_US", "tz": "UTC"})

# Kwargs style (equivalent)
partners_fr = partners.with_context(lang="fr_FR", tz="Europe/Paris")

# Company alias (maps to context keys)
partners_c7 = partners.with_company(7)
# -> context includes: {"allowed_company_ids": [7], "company_id": 7}
```

### OdooEntity

- `id`, `exists()`, `refresh()`
- `get_data(fields=None)`
- `save()`, `delete()`

## Compatibility Notes

- For common ORM methods, limited positional compatibility is provided.
- For custom methods, use named dict payloads:

```python
model = odoo.model("your.model")
result = model.your_method({"param_a": 1, "param_b": "x"})
```

JSON-2 does not support positional arguments for method parameters.

## Database Service

```python
version = odoo.database.version()
dbs = odoo.database.list()
exists = odoo.database.db_exist("mycompany")
```

Includes wrappers:

- `version`, `server_version`, `list`, `db_exist`
- `create_database`, `duplicate_database`, `drop`
- `change_admin_password`, `backup`, `restore`, `neutralize_database`

## Error Handling

- Last error available on `client.error` or `model.error`.
- Set `debug=True` to raise exceptions immediately.

## Supported Odoo Range

- Intended for Odoo 19+ using JSON-2 API.
- RPC deprecation in Odoo 20 is accounted for by using `/json/2` transport.
- For older RPC-based Odoo deployments, use `pyodoo-rpc-client`:
  - PyPI: https://pypi.org/project/pyodoo-rpc-client/
  - GitHub: https://github.com/tumbi-j/pyodoo-rpc-client

## Contributing

- Open Issues for bugs and concrete feature requests.
- Open Pull Requests for code/docs improvements.
- For open-ended questions and ideas, use GitHub Discussions (enable in repo settings).
- See `CONTRIBUTING.md` for workflow and expectations.

## Development

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```
