from __future__ import annotations

from typing import Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import OdooClient


class OdooDatabaseService:
    def __init__(self, client: "OdooClient"):
        self.client = client

    def version(self):
        return self.client.call_web("GET", "/web/version", default={})

    def server_version(self) -> Optional[str]:
        data = self.version() or {}
        if isinstance(data, dict):
            return data.get("version")
        return None

    def list(self):
        res = self.client.call_web(
            "POST",
            "/web/database/list",
            json_data={},
            headers={"Content-Type": "application/json-rpc"},
            default={"result": []},
        )
        if isinstance(res, dict):
            return res.get("result", [])
        if isinstance(res, list):
            return res
        return []

    def db_exist(self, db_name: str) -> bool:
        return db_name in self.list()

    def create_database(
        self,
        master_pwd: str,
        db_name: str,
        demo: bool = False,
        lang: str = "en_US",
        user_password: str = "admin",
        login: str = "admin",
        country_code: str = "US",
        phone: str = "",
    ):
        return self.client.call_web(
            "POST",
            "/web/database/create",
            form_data={
                "master_pwd": master_pwd,
                "name": db_name,
                "login": login,
                "password": user_password,
                "demo": bool(demo),
                "lang": lang,
                "phone": phone,
                "country_code": country_code,
            },
            default=False,
        )

    def duplicate_database(self, master_pwd: str, db_original_name: str, db_name: str, neutralize_database: bool = False):
        return self.client.call_web(
            "POST",
            "/web/database/duplicate",
            form_data={
                "master_pwd": master_pwd,
                "name": db_original_name,
                "new_name": db_name,
                "neutralize_database": bool(neutralize_database),
            },
            default=False,
        )

    def drop(self, master_pwd: str, db_name: str):
        return self.client.call_web(
            "POST",
            "/web/database/drop",
            form_data={"master_pwd": master_pwd, "name": db_name},
            default=False,
        )

    def change_admin_password(self, master_pwd: str, new_password: str):
        return self.client.call_web(
            "POST",
            "/web/database/change_password",
            form_data={"master_pwd": master_pwd, "master_pwd_new": new_password},
            default=False,
        )

    def backup(self, master_pwd: str, db_name: str, backup_format: str = "zip"):
        response = self.client.call_web(
            "POST",
            "/web/database/backup",
            form_data={"master_pwd": master_pwd, "name": db_name, "backup_format": backup_format},
            default=None,
            raw_response=True,
        )
        if response is None:
            return None
        return response.content

    def restore(self, master_pwd: str, db_name: str, backup_file_path: str, copy: bool = False, neutralize: bool = False):
        with open(backup_file_path, "rb") as file_obj:
            return self.client.call_web(
                "POST",
                "/web/database/restore",
                form_data={
                    "master_pwd": master_pwd,
                    "name": db_name,
                    "copy": bool(copy),
                    "neutralize": bool(neutralize),
                },
                files={"backup_file": file_obj},
                default=False,
            )

    def neutralize_database(self, master_pwd: str, db_name: str):
        return self.client.call_web(
            "POST",
            "/web/database/neutralize",
            form_data={"master_pwd": master_pwd, "name": db_name},
            default=False,
        )
