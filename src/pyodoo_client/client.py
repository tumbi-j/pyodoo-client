from __future__ import annotations

import copy
from typing import Any, Dict, Optional, Union

import requests

from .transport.http_adapter import HttpAdapter
from .transport.requests_adapter import RequestsHttpAdapter

from .database import OdooDatabaseService
from .exceptions import OdooApiError, OdooConfigError


class OdooClient:
    def __init__(
        self,
        url: str,
        api_key: Optional[str] = None,
        key: Optional[str] = None,
        db: Optional[str] = None,
        timeout: Union[int, float] = 30,
        verify_ssl: bool = True,
        user_agent: str = "pyodoo-client",
        debug: bool = False,
        default_context: Optional[Dict[str, Any]] = None,
        http_adapter: Optional[HttpAdapter] = None,
        session: Optional[requests.Session] = None,
    ):
        if not url:
            raise OdooConfigError("url is required")

        self.url = self._normalize_url(url)
        self.db = db
        self.key = api_key or key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.user_agent = user_agent
        self.debug = bool(debug)
        self.default_context = copy.deepcopy(default_context or {})

        session = session or requests.Session()
        session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        })
        if self.key:
            session.headers.update({"Authorization": f"bearer {self.key}"})
        if self.db:
            session.headers.update({"X-Odoo-Database": str(self.db)})

        self.http = http_adapter or RequestsHttpAdapter(session=session)
        self.logged_in = False
        self.error = None
        self.uid = None

        self.database = OdooDatabaseService(self)

        self._bootstrap_status()

    @staticmethod
    def _normalize_url(url: str) -> str:
        clean = str(url).rstrip("/")
        if clean.endswith("/json/2"):
            return clean
        return f"{clean}/json/2"

    @property
    def base_http_url(self) -> str:
        if self.url.endswith("/json/2"):
            return self.url[:-7]
        return self.url

    def _bootstrap_status(self):
        if not self.key:
            self.error = OdooConfigError("api_key/key is required")
            self.logged_in = False
            return
        whoami = self.call_model("res.users", "context_get", payload={}, default=None)
        self.uid = whoami.get("uid") if isinstance(whoami, dict) else None
        self.logged_in = isinstance(whoami, dict) and self.error is None

    def set_debug(self, debug: bool):
        self.debug = bool(debug)
        return self

    def set_default_context(self, context: Optional[Dict[str, Any]] = None):
        self.default_context = copy.deepcopy(context or {})
        return self

    def update_default_context(self, context: Optional[Dict[str, Any]] = None):
        if context:
            self.default_context.update(copy.deepcopy(context))
        return self

    def model(self, model_name: str):
        from .model import OdooModel

        return OdooModel(client=self, model_name=model_name)

    @staticmethod
    def _safe_json(response: requests.Response):
        try:
            return response.json()
        except Exception:
            return None

    def _handle_error(self, exc: Exception, default: Any = None, debug: Optional[bool] = None):
        self.error = exc
        should_raise = self.debug if debug is None else bool(debug)
        if should_raise:
            raise exc
        return default

    def _merge_context(self, payload: Optional[Dict[str, Any]], context: Optional[Dict[str, Any]] = None):
        data = copy.deepcopy(payload or {})
        merged_context = {}
        if self.default_context:
            merged_context.update(self.default_context)
        if isinstance(data.get("context"), dict):
            merged_context.update(data["context"])
        if context:
            merged_context.update(context)
        if merged_context:
            data["context"] = merged_context
        return data

    def call_model(
        self,
        model_name: str,
        method: str,
        payload: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        debug: Optional[bool] = None,
        default: Any = None,
    ):
        url = f"{self.url}/{model_name}/{method}"
        data = self._merge_context(payload, context)
        try:
            response = self.http.post(
                url,
                json=data,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            if response.status_code >= 400:
                error_payload = self._safe_json(response)
                message = "Odoo API request failed"
                if isinstance(error_payload, dict):
                    message = error_payload.get("message") or error_payload.get("name") or message
                raise OdooApiError(
                    message=message,
                    status_code=response.status_code,
                    payload=error_payload if isinstance(error_payload, dict) else None,
                    response_text=response.text,
                )

            parsed = self._safe_json(response)
            if parsed is None:
                return default
            self.error = None
            return parsed
        except Exception as exc:
            return self._handle_error(exc, default=default, debug=debug)

    def call_web(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        debug: Optional[bool] = None,
        default: Any = None,
        raw_response: bool = False,
    ):
        url = f"{self.base_http_url}{path}"
        request_headers = dict(headers or {})
        if json_data is not None and "Content-Type" not in request_headers:
            request_headers["Content-Type"] = "application/json; charset=utf-8"
        if form_data is not None and files is None and "Content-Type" not in request_headers:
            request_headers["Content-Type"] = "application/x-www-form-urlencoded"

        try:
            response = self.http.request(
                method=method,
                url=url,
                json=json_data,
                data=form_data,
                files=files,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            if response.status_code >= 400:
                error_payload = self._safe_json(response)
                message = "Odoo web endpoint request failed"
                if isinstance(error_payload, dict):
                    message = error_payload.get("message") or error_payload.get("name") or message
                raise OdooApiError(
                    message=message,
                    status_code=response.status_code,
                    payload=error_payload if isinstance(error_payload, dict) else None,
                    response_text=response.text,
                )
            if raw_response:
                self.error = None
                return response
            parsed = self._safe_json(response)
            self.error = None
            return parsed if parsed is not None else default
        except Exception as exc:
            return self._handle_error(exc, default=default, debug=debug)
