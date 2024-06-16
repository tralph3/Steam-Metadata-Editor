import textvdf
from os import path


AppID = int
LibID = str


class AppNotInstalledError(Exception):
    pass

class NoManifestError(Exception):
    pass

class SteamLibraries:
    def __init__(self, steam_install_path):
        self._steam_install_path = steam_install_path
        libraryfolders_path = path.join(self._steam_install_path, "steamapps", "libraryfolders.vdf")
        self._libraryfolders = textvdf.loads(libraryfolders_path)["libraryfolders"]
        self._appinfo: dict[AppID, dict] = {}
        self._populate_appinfo()

    def _populate_appinfo(self):
        for library in self._libraryfolders:
            for appid in self._libraryfolders[library]["apps"]:
                appid = int(appid)
                self._appinfo.setdefault(appid, {})
                manifest = self._get_app_manifest(appid, library)
                installdir = manifest["AppState"]["installdir"]
                librarypath = self._get_library_path(library)
                installpath = path.join(librarypath, "steamapps", "common", installdir)
                self._appinfo[appid]["installpath"] = installpath
                for depot in manifest["AppState"].get("InstalledDepots", {}):
                    depot = int(depot)
                    self._appinfo.setdefault(depot, {})
                    self._appinfo[depot]["installpath"] = installpath

    def _get_library_path(self, libraryid: LibID) -> str:
        return self._libraryfolders[libraryid]["path"]

    def _get_app_manifest(self, appid: AppID, libraryid: LibID) -> dict:
        library_path = self._get_library_path(libraryid)
        manifest_path = path.join(library_path, "steamapps", f"appmanifest_{appid}.acf")
        if not path.exists(manifest_path):
            raise NoManifestError(f"App '{appid}' has no manifest file at '{manifest_path}'")
        return textvdf.loads(manifest_path)

    def is_app_installed(self, appid: AppID) -> bool:
        return appid in self._appinfo

    def get_app_install_path(self, appid: AppID) -> str:
        if not self.is_app_installed(appid):
            raise AppNotInstalledError(f"App '{appid}' is not installed")
        return self._appinfo[appid]["installpath"]
