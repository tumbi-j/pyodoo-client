import json
from typing import Any, Dict, Optional
from .http_adapter import HttpAdapter


class DatabricksHttpResponse:
    def __init__(self, status_code: int, text: str = "", headers: Optional[Dict[str, Any]] = None):
        self.status_code = int(status_code)
        self.text = text or ""
        self.headers = dict(headers or {})

    def json(self):
        return json.loads(self.text or "{}")


class DatabricksHttpAdapter(HttpAdapter):
    def __init__(self, spark, connection_name: str):
        self.spark = spark
        self.connection_name = connection_name

    @staticmethod
    def _sql_escape(value: Any) -> str:
        return str(value).replace("'", "''")

    @staticmethod
    def _normalize_headers(headers: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        normalized = {"Content-Type": "application/json"}
        for key, value in (headers or {}).items():
            normalized[str(key)] = str(value)
        return normalized

    @classmethod
    def _headers_map_sql(cls, headers: Optional[Dict[str, Any]] = None) -> str:
        normalized = cls._normalize_headers(headers)
        items = []
        for key, value in normalized.items():
            items.append(f"'{cls._sql_escape(key)}'")
            items.append(f"'{cls._sql_escape(value)}'")
        return f"map({', '.join(items)})"

    def _http_request(
        self,
        method: str,
        url: str,
        body_payload: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        body = json.dumps(body_payload or {})
        headers_sql = self._headers_map_sql(headers)
        query = f"""
        SELECT
            http_response_status,
            http_response_body,
            http_response_headers
        FROM
            http_request(
                method => '{self._sql_escape(method.upper())}',
                url => '{self._sql_escape(url)}',
                headers => {headers_sql},
                body => '{self._sql_escape(body)}',
                connection => '{self._sql_escape(self.connection_name)}'
            )
        """
        row = self.spark.sql(query).collect()[0]
        row_data = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        status_code = int(row_data.get("http_response_status", 0))
        response_text = row_data.get("http_response_body") or ""
        response_headers = row_data.get("http_response_headers") or {}
        return DatabricksHttpResponse(
            status_code=status_code,
            text=response_text,
            headers=response_headers if isinstance(response_headers, dict) else {},
        )

    def post(self, url, json=None, headers=None, timeout=None, verify=True):
        return self._http_request(method="POST", url=url, body_payload=json, headers=headers)

    def request(self, method, url, json=None, data=None, files=None, headers=None, timeout=None, verify=True):
        if files:
            raise NotImplementedError("DatabricksHttpAdapter does not support multipart file uploads")
        return self._http_request(method=method, url=url, body_payload=json if json is not None else data, headers=headers)