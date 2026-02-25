from __future__ import annotations

import copy
from typing import Any, Dict, Optional
from typing import TYPE_CHECKING

from .entity import OdooEntity

if TYPE_CHECKING:
    from .client import OdooClient


class OdooModel:
    def __init__(
        self,
        client: "OdooClient",
        model_name: str,
        context: Optional[Dict[str, Any]] = None,
        debug: Optional[bool] = None,
    ):
        self.client = client
        self.model = model_name
        self.context = copy.deepcopy(context or {})
        self.error = None
        self._fields = None
        self._debug = client.debug if debug is None else bool(debug)

    def set_debug(self, debug: bool):
        self._debug = bool(debug)
        return self

    def with_context(self, context: Optional[Dict[str, Any]] = None, **kwargs):
        merged = copy.deepcopy(self.context)
        if context:
            merged.update(copy.deepcopy(context))
        if kwargs:
            merged.update(copy.deepcopy(kwargs))
        return self.__class__(
            client=self.client,
            model_name=self.model,
            context=merged,
            debug=self._debug,
        )

    def with_company(self, company: Any):
        company_ids = self._normalize_ids(company)
        if not company_ids:
            return self.with_context()
        return self.with_context(
            allowed_company_ids=company_ids,
            company_id=company_ids[0],
        )

    def _normalize_ids(self, ids: Any):
        if ids is None:
            return []
        if isinstance(ids, (int, str)):
            return [int(ids)]
        if isinstance(ids, tuple):
            ids = list(ids)
        if isinstance(ids, list):
            if len(ids) == 1 and isinstance(ids[0], list):
                ids = ids[0]
            parsed = []
            for item in ids:
                try:
                    parsed.append(int(item))
                except Exception:
                    continue
            return parsed
        return ids

    @staticmethod
    def _normalize_domain(domain: Any):
        if isinstance(domain, list) and len(domain) == 1 and isinstance(domain[0], list):
            return domain[0]
        return domain

    @staticmethod
    def _default_method_return(method: str):
        method = method.lower()
        if method in {"search", "search_read", "read"}:
            return []
        if method in {"fields_get"}:
            return {}
        if method in {"write", "unlink"}:
            return False
        if method in {"create"}:
            return None
        return []

    def _build_payload(self, method: str, args: tuple, kwargs: dict):
        if len(args) == 1 and isinstance(args[0], dict) and not kwargs and method.lower() != "create":
            return copy.deepcopy(args[0])

        payload = {}
        lower_method = method.lower()

        if lower_method in {"search", "search_read"}:
            if len(args) >= 1:
                payload["domain"] = self._normalize_domain(args[0])
            if len(args) >= 2 and isinstance(args[1], dict):
                payload.update(args[1])
        elif lower_method == "read":
            if len(args) >= 1:
                payload["ids"] = self._normalize_ids(args[0])
            if len(args) >= 2 and isinstance(args[1], dict):
                payload.update(args[1])
        elif lower_method == "create":
            if len(args) >= 1:
                first = args[0]
                if isinstance(first, tuple):
                    first = list(first)
                if isinstance(first, dict):
                    payload["vals_list"] = [first]
                elif isinstance(first, list):
                    if len(first) == 1 and isinstance(first[0], dict):
                        payload["vals_list"] = first
                    elif first and all(isinstance(i, dict) for i in first):
                        payload["vals_list"] = first
                    else:
                        payload["vals"] = first
        elif lower_method == "write":
            ids_arg = args[0] if len(args) >= 1 else None
            vals_arg = args[1] if len(args) >= 2 else None

            if len(args) == 1 and isinstance(args[0], (list, tuple)) and len(args[0]) >= 2:
                ids_arg = args[0][0]
                vals_arg = args[0][1]

            if ids_arg is not None:
                payload["ids"] = self._normalize_ids(ids_arg)
            if vals_arg is not None:
                vals = vals_arg
                if isinstance(vals, list) and len(vals) == 1 and isinstance(vals[0], dict):
                    vals = vals[0]
                payload["vals"] = vals
        elif lower_method == "unlink":
            if len(args) >= 1:
                payload["ids"] = self._normalize_ids(args[0])
        elif lower_method == "fields_get":
            if len(args) >= 1 and isinstance(args[0], dict):
                payload.update(args[0])
            elif len(args) >= 2 and isinstance(args[1], dict):
                payload.update(args[1])
        elif args and not kwargs:
            raise ValueError(
                "JSON-2 requires named parameters. "
                "For custom methods pass a dict payload, e.g. model.my_method({'param': value})."
            )

        if kwargs:
            payload.update(copy.deepcopy(kwargs))
        return payload

    def execute(self, method: str, *args, **kwargs):
        lower_method = method.lower()
        single_create_dict = lower_method == "create" and len(args) == 1 and isinstance(args[0], dict)
        default = self._default_method_return(method)
        try:
            payload = self._build_payload(method, args, kwargs)
        except Exception as exc:
            self.error = exc
            if self._debug:
                raise
            return default

        result = self.client.call_model(
            model_name=self.model,
            method=method,
            payload=payload,
            context=self.context,
            debug=self._debug,
            default=default,
        )

        if isinstance(self.client.error, Exception):
            self.error = self.client.error
        else:
            self.error = None

        if single_create_dict and isinstance(result, list) and len(result) == 1:
            return result[0]

        return result

    def execute_kw(self, method: str, *args, **kwargs):
        return self.execute(method, *args, **kwargs)

    def fields(self):
        if self._fields is None:
            data = self.fields_get({"attributes": ["string", "help", "type", "required", "relation"]})
            self._fields = data if isinstance(data, dict) else {}
        return self._fields

    def search_read(self, *args, **kwargs):
        results = self.execute("search_read", *args, **kwargs)
        if not isinstance(results, list):
            return []
        return [OdooEntity(self, data) for data in results]

    def read(self, *args, **kwargs):
        results = self.execute("read", *args, **kwargs)
        if not isinstance(results, list):
            return []
        return [OdooEntity(self, data) for data in results]

    def get(self, pk):
        return OdooEntity(self, pk)

    def entity(self, data):
        return OdooEntity(self, data)

    def new(self):
        return OdooEntity(self)

    def __getattr__(self, method):
        def function(*_args, **_kwargs):
            return self.execute(method, *_args, **_kwargs)

        return function
