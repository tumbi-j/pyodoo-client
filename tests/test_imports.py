from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class PublicExportsTests(unittest.TestCase):
    def test_public_exports_importable(self):
        from pyodoo_client import OdooApiError, OdooClient, OdooConfigError, OdooEntity, OdooModel

        self.assertIsNotNone(OdooClient)
        self.assertIsNotNone(OdooModel)
        self.assertIsNotNone(OdooEntity)
        self.assertIsNotNone(OdooApiError)
        self.assertIsNotNone(OdooConfigError)
