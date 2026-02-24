from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OdooApiError(Exception):
    message: str
    status_code: Optional[int] = None
    payload: Optional[Dict[str, Any]] = None
    response_text: Optional[str] = None

    def __str__(self) -> str:
        if self.status_code is None:
            return self.message
        return f"{self.status_code}: {self.message}"


class OdooConfigError(ValueError):
    pass
