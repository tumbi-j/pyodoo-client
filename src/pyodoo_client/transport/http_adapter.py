from typing import Any, Dict, Optional


class HttpAdapter:
    def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: bool = True
    ) -> Any:
        raise NotImplementedError("HttpAdapter.post must be implemented by subclasses")
    def request(
        self,
        method: str,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: bool = True
    ) -> Any:
        raise NotImplementedError("HttpAdapter.request must be implemented by subclasses")