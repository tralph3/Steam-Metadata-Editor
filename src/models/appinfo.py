from typing import Optional
import appinfo

class AppinfoFile:
    def __init__(self, file_path):
        self._file_path = file_path
        self._appinfo = appinfo.loads(file_path)

    def write(self):
        with open(self._file_path, "wb") as f:
            appinfo.dump(self._appinfo, f)

    def get_all_apps(self) -> dict:
        return self._appinfo["apps"]

    def get_app_count(self) -> int:
        return len(self._appinfo["apps"])

    def set_app_name(self, appid: int, name: str):
        self._appinfo["apps"][appid]["content"]["appinfo"]["common"]["name"] = name

    def get_app_name(self, appid: int) -> Optional[str]:
        try:
            return self._appinfo["apps"][appid]["content"]["appinfo"]["common"]["name"]
        except KeyError:
            return None

    def set_app_sortas(self, appid: int, sortas: str):
        self._appinfo["apps"][appid]["content"]["appinfo"]["common"]["sortas"] = sortas

    def get_app_sortas(self, appid: int) -> Optional[str]:
        try:
            return self._appinfo["apps"][appid]["content"]["appinfo"]["common"]["sortas"]
        except KeyError:
            return None

    def get_app_type(self, appid: int) -> Optional[str]:
        try:
            return self._appinfo["apps"][appid]["content"]["appinfo"]["common"]["type"]
        except KeyError:
            return None

    def set_app_steam_release_date(self, appid: int, release_date: int):
        self._appinfo["apps"][appid]["content"]["appinfo"]["common"]["steam_release_date"] = release_date

    def get_app_steam_release_date(self, appid: int) -> Optional[int]:
        try:
            return self._appinfo["apps"][appid]["content"]["appinfo"]["common"]["steam_release_date"]
        except KeyError:
            return None

    def set_app_original_release_date(self, appid: int, release_date: int):
        self._appinfo["apps"][appid]["content"]["appinfo"]["common"]["original_release_date"] = release_date

    def get_app_original_release_date(self, appid: int) -> Optional[int]:
        try:
            return self._appinfo["apps"][appid]["content"]["appinfo"]["common"]["original_release_date"]
        except KeyError:
            return None

    def set_app_launch_menu(self, appid: int, launch_menu: dict):
        self._appinfo["apps"][appid]["content"]["appinfo"].setdefault("config", {})
        self._appinfo["apps"][appid]["content"]["appinfo"]["config"]["launch"] = launch_menu

    def get_app_launch_menu(self, appid: int) -> Optional[dict]:
        try:
            return self._appinfo["apps"][appid]["content"]["appinfo"]["config"]["launch"]
        except KeyError:
            return None
