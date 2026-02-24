from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pyodoo_client import OdooClient
from pyodoo_client.exceptions import OdooApiError


class DummyResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("No JSON payload")
        return self._payload


class DummySession:
    def __init__(self, responses):
        self._responses = list(responses)
        self.headers = {}
        self.calls = []

    def post(self, url, json=None, headers=None, timeout=None, verify=None):
        self.calls.append(
            {
                "url": url,
                "json": json,
                "headers": headers,
                "timeout": timeout,
                "verify": verify,
            }
        )
        return self._responses.pop(0)


class OdooClientBehaviorTests(unittest.TestCase):
    def test_call_model_merges_default_and_request_context(self):
        session = DummySession(
            responses=[
                DummyResponse(200, {"uid": 42}),
                DummyResponse(200, {"ok": True}),
            ]
        )

        client = OdooClient(
            url="https://example.com",
            api_key="token",
            db="testdb",
            default_context={"lang": "en_US"},
            session=session,
        )

        result = client.call_model(
            model_name="res.partner",
            method="search_read",
            payload={"domain": [], "context": {"allowed_company_ids": [1]}},
            context={"tz": "UTC"},
        )

        self.assertEqual(result, {"ok": True})
        request_payload = session.calls[1]["json"]
        self.assertEqual(request_payload["context"]["lang"], "en_US")
        self.assertEqual(request_payload["context"]["allowed_company_ids"], [1])
        self.assertEqual(request_payload["context"]["tz"], "UTC")

    def test_call_model_returns_default_when_debug_false_on_http_error(self):
        session = DummySession(
            responses=[
                DummyResponse(200, {"uid": 1}),
                DummyResponse(500, {"message": "boom"}, text="boom"),
            ]
        )

        client = OdooClient(
            url="https://example.com",
            api_key="token",
            session=session,
            debug=False,
        )

        default_value = []
        result = client.call_model("res.partner", "search_read", payload={"domain": []}, default=default_value)

        self.assertEqual(result, default_value)
        self.assertIsInstance(client.error, OdooApiError)
